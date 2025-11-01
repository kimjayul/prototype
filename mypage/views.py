from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from posts.models import Post
from .serializers import (
    UserProfileSerializer, 
    UserUpdateSerializer, 
    ChangePasswordSerializer,
    MyPostSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

# ========== 프로필 관련 ==========

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """내 프로필 조회 및 수정"""
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """비밀번호 변경"""
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        
        # 현재 비밀번호 확인
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': '현재 비밀번호가 일치하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 새 비밀번호 설정
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # 세션 유지
        update_session_auth_hash(request, user)
        
        return Response({'message': '비밀번호가 변경되었습니다.'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_statistics(request):
    """내 통계 조회"""
    user = request.user
    stats = {
        'total_posts': Post.objects.filter(author=user).count(),
        'total_likes': 0,
        'total_comments': 0,
    }
    return Response(stats)

# ========== 내 게시물 관련 ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts(request):
    """내 게시물 전체 조회"""
    user = request.user
    
    # 내 게시물만 필터링
    posts = Post.objects.filter(author=user)
    
    # 검색
    search = request.query_params.get('search', None)
    if search:
        posts = posts.filter(title__icontains=search) | posts.filter(content__icontains=search)
    
    # 정렬
    ordering = request.query_params.get('ordering', '-created_at')
    posts = posts.order_by(ordering)
    
    # 페이지네이션
    paginator = StandardResultsSetPagination()
    paginated_posts = paginator.paginate_queryset(posts, request)
    
    serializer = MyPostSerializer(paginated_posts, many=True)
    return paginator.get_paginated_response(serializer.data)
