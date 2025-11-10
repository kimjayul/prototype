# posts/views.py (FINAL_BACKEND + mypage 통합)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from .serializers import PostSerializer, PostDetailSerializer, FavoritePostSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, PostLike


# ==================== 기존 뷰들 (FINAL_BACKEND 유지!) ====================

class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})  # ✅ context 유지
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    # ✅ FINAL_BACKEND 기능 유지
    def get_serializer_context(self):
        """request를 serializer context에 추가"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # ✅ FINAL_BACKEND 기능 유지
    
    def get(self, request, post_id):
        """게시글 수정을 위해 기존 데이터를 불러옵니다."""
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({'error': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = PostSerializer(post, context={'request': request})  # ✅ context 유지
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, post_id):  # ✅ FINAL_BACKEND의 patch 유지
        """수정된 내용을 데이터베이스에 저장합니다."""
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({'error': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = PostSerializer(post, data=request.data, 
                                       partial=True,  # ✅ FINAL_BACKEND 기능 유지
                                       context={'request': request})  # ✅ context 유지
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            # ✅ mypage의 is_superuser 체크 추가
            if (post.author != request.user) and (not request.user.is_staff) and (not request.user.is_superuser):
                return Response({'error': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            post.delete()
            return Response({'message': '게시글이 삭제되었습니다.'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


# ==================== 여기서부터 mypage 새로 추가! ====================

class StandardResultsSetPagination(PageNumberPagination):
    """표준 페이지네이션"""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class MyPostsListView(generics.ListAPIView):
    """내 게시물 목록 조회"""
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(author=user)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'created_at':
            queryset = queryset.order_by('created_at')
        elif ordering == '-created_at':
            queryset = queryset.order_by('-created_at')
        elif ordering == 'likes_count':
            queryset = queryset.annotate(
                likes_count_field=Count('post_likes')
            ).order_by('likes_count_field')
        elif ordering == '-likes_count':
            queryset = queryset.annotate(
                likes_count_field=Count('post_likes')
            ).order_by('-likes_count_field')
        
        return queryset


class FavoritePostsListView(generics.ListAPIView):
    """내가 좋아요한 게시물 목록 조회"""
    serializer_class = FavoritePostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        return PostLike.objects.filter(user=user).select_related('post', 'post__author')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, post_id):
    """게시물 좋아요 토글"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {"error": "게시물을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user = request.user
    like, created = PostLike.objects.get_or_create(user=user, post=post)
    
    if not created:
        like.delete()
        return Response(
            {"message": "좋아요가 취소되었습니다.", "is_liked": False},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"message": "좋아요를 눌렀습니다.", "is_liked": True},
            status=status.HTTP_201_CREATED
        )
