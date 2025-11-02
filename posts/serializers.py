from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    postId = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Post
        fields = ['postId', 'title', 'content', 'author', 'created_at', 'audio_file', 'image', 
                  'view_count', 'like_count']  # ⭐ 이 2개 추가!
        read_only_fields = ['author', 'created_at', 'view_count', 'like_count']  # ⭐ 추가!
    
