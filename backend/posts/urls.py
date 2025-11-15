from django.urls import path
from .views import PostCreateView, PostListView

urlpatterns = [
    path('create-post/', PostCreateView.as_view(), name='create-post'),
    path('list-posts/', PostListView.as_view(), name='list-posts'),
]