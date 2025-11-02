from django.urls import path
from .views import MyMusicListView, FavoriteMusicListView, toggle_music_like

urlpatterns = [
    # 내 음악 목록
    path('my-music/', MyMusicListView.as_view(), name='my-music'),
    
    # 좋아요한 음악 목록
    path('favorites/', FavoriteMusicListView.as_view(), name='favorite-music'),
    
    # 음악 좋아요 토글
    path('<int:music_id>/like/', toggle_music_like, name='toggle-music-like'),
]
