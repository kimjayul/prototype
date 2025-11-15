from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PostSerializer
from .models import Post

class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data)
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