# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import RegisterView, LoginView, UserView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]
