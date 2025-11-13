# posts/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics  # ✅ generics 임포트
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination  # ✅ 페이지네이션 임포트
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count  # ✅ Q, Count 임포트
# ✅ 필요한 시리얼라이저 모두 임포트
from .serializers import PostSerializer, PostDetailSerializer, FavoritePostSerializer
from .models import Post, PostLike


# ==================== 기존 뷰들 ====================

class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_serializer_context(self):
        """request를 serializer context에 추가"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PostDetailView(RetrieveAPIView):
    """게시물 상세 조회 (✅ 현재 코드의 신규 기능 유지)"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer  # ✅ 상세 조회가 PostSerializer를 사용
    lookup_field = 'id'
    lookup_url_kwarg = 'post_id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, post_id):
        """게시글 수정을 위해 기존 데이터를 불러옵니다."""
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({'error': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, post_id):
        """수정된 내용을 데이터베이스에 저장합니다."""
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({'error': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

            serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            # ✅ 이전 'mypage 통합' 버전의 'superuser' 삭제 권한 로직 적용
            if (post.author != request.user) and (not request.user.is_staff) and (not request.user.is_superuser):
                return Response({'error': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            post.delete()
            return Response({'message': '게시글이 삭제되었습니다.'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


# ==================== 마이페이지용 (기능 통합) ====================

class StandardResultsSetPagination(PageNumberPagination):
    """✅ 표준 페이지네이션 (이전 'mypage 통합' 버전)"""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class MyPostsListView(generics.ListAPIView):
    """
    ✅ 내가 작성한 게시물 목록 (이전 'mypage 통합' 버전의
    페이지네이션, 검색, 고급 정렬 기능 적용)
    """
    serializer_class = PostDetailSerializer  # ✅ PostDetailSerializer 사용
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # ✅ 페이지네이션 적용

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(author=user)

        # ✅ 검색 기능
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # ✅ 고급 정렬 기능 (좋아요순 포함)
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'created_at':
            queryset = queryset.order_by('created_at')
        elif ordering == '-created_at':
            queryset = queryset.order_by('-created_at')
        elif ordering == 'likes_count':
            queryset = queryset.annotate(
                likes_count_field=Count('post_likes')
            ).order_by('likes_count_field')
        elif ordering == '-likes_count':
            queryset = queryset.annotate(
                likes_count_field=Count('post_likes')
            ).order_by('-likes_count_field')

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FavoritePostsListView(generics.ListAPIView):
    """
    ✅ 좋아요한 게시물 목록 (이전 'mypage 통합' 버전의
    페이지네이션, 전용 시리얼라이저 적용)
    """
    serializer_class = FavoritePostSerializer  # ✅ FavoritePostSerializer 사용
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # ✅ 페이지네이션 적용

    def get_queryset(self):
        user = self.request.user
        # ✅ 'mypage 통합' 버전의 쿼리 (FavoritePostSerializer와 짝)
        return PostLike.objects.filter(user=user).select_related('post', 'post__author')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, post_id):
    """✅ 게시물 좋아요 토글 (현재 코드의 'likes_count' 응답 기능 유지)"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {"error": "게시물을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )

    like, created = PostLike.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        # 이미 좋아요가 있으면 삭제 (토글)
        like.delete()
        return Response(
            {
                "message": "좋아요 취소",
                "is_liked": False,
                "likes_count": post.post_likes.count()  # ✅ 카운트 포함
            },
            status=status.HTTP_200_OK
        )
    else:
        # 새로 좋아요 추가
        return Response(
            {
                "message": "좋아요 추가",
                "is_liked": True,
                "likes_count": post.post_likes.count()  # ✅ 카운트 포함
            },
            status=status.HTTP_201_CREATED
        )
