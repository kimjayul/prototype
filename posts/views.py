# posts/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView  # ✅ RetrieveAPIView 추가
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PostSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post


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


# ✅ 새로 추가된 클래스
class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'              # 👈 URL에서 ID를 찾는 필드 이름 (기본값 pk)
    lookup_url_kwarg = 'post_id'     # 👈 urls.py에서 사용할 변수 이름


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
    
    def patch(self, request, post_id):  # ⭐️ put → patch로 변경
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
