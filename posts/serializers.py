from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, PostLike


# ==================== 기존 PostSerializer (그대로 유지!) ====================
class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    postId = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Post
        fields = ['postId', 'title', 'content', 'author', 'created_at', 'audio_file', 'image', 
                  'view_count', 'like_count']
        read_only_fields = ['author', 'created_at', 'view_count', 'like_count']


# ==================== 여기서부터 새로 추가! ====================

class PostAuthorSerializer(serializers.ModelSerializer):
    """게시물 작성자 정보 (간단 버전)"""
    class Meta:
        model = User
        fields = ['id', 'username']


class PostDetailSerializer(serializers.ModelSerializer):
    """게시물 상세 시리얼라이저 (MyPage용)"""
    author = PostAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'audio_file', 'image',
                  'created_at', 'likes_count', 'is_liked', 'view_count', 'like_count']
        read_only_fields = ['id', 'created_at', 'author', 'view_count', 'like_count']
    
    def get_is_liked(self, obj):
        """현재 사용자가 좋아요 했는지 확인"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False


class FavoritePostSerializer(serializers.ModelSerializer):
    """좋아요한 게시물 시리얼라이저"""
    post = PostDetailSerializer(read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']
