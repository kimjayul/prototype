# accounts/views.py

from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserStatisticsSerializer
)


# ==================== 기존 코드 (그대로 유지!) ====================

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
            token.blacklist()
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

class UserProfileView(generics.RetrieveUpdateAPIView):
    """내 프로필 조회 및 수정"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """비밀번호 변경"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
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
    
    stats = {
        'total_posts': user.post_set.count(),
        'total_music': user.music_works.count(),
        'total_likes': sum([post.likes_count for post in user.post_set.all()]) + 
                       sum([music.likes_count for music in user.music_works.all()]),
        'total_comments': 0,
        'total_favorites': user.post_likes.count() + user.music_likes.count(),
    }
    
    serializer = UserStatisticsSerializer(stats)
    return Response(serializer.data, status=status.HTTP_200_OK)
