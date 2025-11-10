from django.urls import path
from .views import (
    PostCreateView, 
    PostListView, 
    PostDeleteView, 
    PostUpdateView,
    MyPostsListView,
    FavoritePostsListView,
    toggle_post_like,
)

urlpatterns = [
    # ==================== 기존 URL (그대로 유지!) ====================
    path('create-post/', PostCreateView.as_view(), name='create-post'),
    path('list-posts/', PostListView.as_view(), name='list-posts'),
    path('delete-post/<int:post_id>/', PostDeleteView.as_view(), name='delete-post'),
    path('update-post/<int:post_id>/', PostUpdateView.as_view(), name='update-post'),
    
    # ==================== 여기서부터 새로 추가! ====================
    path('my-posts/', MyPostsListView.as_view(), name='my-posts'),
    path('favorites/', FavoritePostsListView.as_view(), name='favorite-posts'),
    path('<int:post_id>/like/', toggle_post_like, name='toggle-post-like'),
]
