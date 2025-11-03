# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import (
    RegisterView, 
    LoginView, 
    UserView, 
    LogoutView,
    UserProfileView,
    change_password,
    user_statistics
)

urlpatterns = [
    # ==================== 기존 URL (그대로 유지!) ====================
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # ==================== 여기서부터 새로 추가! ====================
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', change_password, name='change-password'),
    path('me/statistics/', user_statistics, name='user-statistics'),
]
