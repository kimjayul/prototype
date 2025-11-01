from django.urls import path
from . import views

urlpatterns = [
    # 프로필 관련
    path('users/me/', views.my_profile, name='my-profile'),
    path('users/change-password/', views.change_password, name='change-password'),
    path('users/me/statistics/', views.my_statistics, name='my-statistics'),
    
    # 게시물 관련
    path('posts/my-posts/', views.my_posts, name='my-posts'),
]
