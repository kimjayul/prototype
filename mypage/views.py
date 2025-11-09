from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from .models import Music, MusicLike
from .serializers import MusicSerializer, FavoriteMusicSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """표준 페이지네이션"""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class MyMusicListView(generics.ListAPIView):
    """내 음악 목록 조회"""
    serializer_class = MusicSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Music.objects.filter(author=user)
        
        # 검색
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(genre__icontains=search)
            )
        
        # 정렬
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        
        return queryset


class FavoriteMusicListView(generics.ListAPIView):
    """내가 좋아요한 음악 목록 조회"""
    serializer_class = FavoriteMusicSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        return MusicLike.objects.filter(user=user).select_related('music', 'music__author')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_music_like(request, music_id):
    """음악 좋아요 토글"""
    try:
        music = Music.objects.get(id=music_id)
    except Music.DoesNotExist:
        return Response(
            {"error": "음악을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user = request.user
    like, created = MusicLike.objects.get_or_create(user=user, music=music)
    
    if not created:
        # 이미 좋아요가 있으면 삭제 (토글)
        like.delete()
        return Response(
            {"message": "좋아요가 취소되었습니다.", "is_liked": False},
            status=status.HTTP_200_OK
        )
    else:
        # 새로 좋아요 추가
        return Response(
            {"message": "좋아요를 눌렀습니다.", "is_liked": True},
            status=status.HTTP_201_CREATED
        )
