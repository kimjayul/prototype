# accounts/urls_mypage.py (추가)
from django.urls import path
from .views import UserProfileView, change_password, user_statistics

# mypage 관련 URL만!
urlpatterns = [
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', change_password, name='change-password'),
    path('me/statistics/', user_statistics, name='user-statistics'),
    path('<int:pk>/', UserProfileView.as_view(), name='user-detail'),
]
