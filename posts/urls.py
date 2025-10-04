from django.urls import path
from .views import PostCreateView, PostListView, PostDeleteView

urlpatterns = [
    path('create-post/', PostCreateView.as_view(), name='create-post'),
    path('list-posts/', PostListView.as_view(), name='list-posts'),
    path('delete-post/<int:post_id>/', PostDeleteView.as_view(), name='delete-post'),
]