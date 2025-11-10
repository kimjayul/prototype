# posts/urls.py

from django.urls import path
from .views import PostCreateView, PostListView, PostDeleteView, PostUpdateView, PostDetailView

urlpatterns = [
    path('create-post/', PostCreateView.as_view(), name='create-post'),
    path('list-posts/', PostListView.as_view(), name='list-posts'),
    path('delete-post/<int:post_id>/', PostDeleteView.as_view(), name='delete-post'),
    
    # ❗️ 'posts/' 접두사 제거
    path('<int:post_id>/', PostDetailView.as_view(), name='post-detail'), 
    
    # ❗️ 'posts/' 접두사 제거
    path('update-post/<int:post_id>/', PostUpdateView.as_view(), name='post-update'),
]