# accounts/views.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

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
