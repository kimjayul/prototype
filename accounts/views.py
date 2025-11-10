# accounts/views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
from .models import Profile


# ==================== 기존 뷰들 (그대로 유지!) ====================

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username') 
        password = request.data.get('password')
        nickname = request.data.get('nickname')  
        if User.objects.filter(username=username).exists():
            return Response({'error': '이미 존재하는 사용자입니다.'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        user.first_name = nickname  
        user.save()
        return Response({'message': '회원가입 성공'}, status=201)
    

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': '인증 실패'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    

class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "refresh_token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # 토큰 블랙리스트 등록
            return Response({"message": "로그아웃 완료"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        

class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({
            'username': request.user.username,
            'id': request.user.id
        })


# ==================== 여기서부터 새로 추가! ====================

class UserProfileView(APIView):
    """사용자 프로필 조회 및 수정"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """프로필 조회"""
        if pk:
            # 다른 사용자 프로필 조회
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response(
                    {"error": "사용자를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # 내 프로필 조회
            user = request.user
        
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """프로필 수정"""
        user = request.user
        serializer = UserProfileSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """프로필 부분 수정"""
        return self.put(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """비밀번호 변경"""
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_statistics(request):
    """사용자 통계 조회"""
    user = request.user
    
    # 게시물 수
    total_posts = user.post_set.count()
    
    # 음악 수
    total_music = user.music_works.count() if hasattr(user, 'music_works') else 0
    
    # 좋아요 받은 수
    total_likes = 0
    if hasattr(user, 'post_set'):
        for post in user.post_set.all():
            total_likes += post.post_likes.count()
    if hasattr(user, 'music_works'):
        for music in user.music_works.all():
            total_likes += music.music_likes.count()
    
    # 댓글 수 (댓글 모델이 있다면)
    total_comments = 0
    
    # 좋아요한 게시물/음악 수
    total_favorites = 0
    if hasattr(user, 'post_likes'):
        total_favorites += user.post_likes.count()
    if hasattr(user, 'music_likes'):
        total_favorites += user.music_likes.count()
    
    stats = {
        'total_posts': total_posts,
        'total_music': total_music,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_favorites': total_favorites,
    }
    
    return Response(stats, status=status.HTTP_200_OK)
