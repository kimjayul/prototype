# posts/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PostSerializer
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
    """게시물 상세 조회"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
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
            if (post.author != request.user) and (not request.user.is_staff):
                return Response({'error': '삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
            post.delete()
            return Response({'message': '게시글이 삭제되었습니다.'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


# ==================== 마이페이지용 추가 뷰들 ====================

class MyPostsListView(ListAPIView):
    """내가 작성한 게시물 목록"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FavoritePostsListView(ListAPIView):
    """좋아요한 게시물 목록"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # 사용자가 좋아요한 게시물만 필터링
        return Post.objects.filter(post_likes__user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, post_id):
    """게시물 좋아요 토글"""
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
                "likes_count": post.post_likes.count()
            },
            status=status.HTTP_200_OK
        )
    else:
        # 새로 좋아요 추가
        return Response(
            {
                "message": "좋아요 추가",
                "is_liked": True,
                "likes_count": post.post_likes.count()
            },
            status=status.HTTP_201_CREATED
        )
