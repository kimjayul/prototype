from rest_framework import serializers
from django.contrib.auth.models import User
from posts.models import Post

class UserProfileSerializer(serializers.ModelSerializer):
    """유저 프로필 시리얼라이저"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'posts_count']
        read_only_fields = ['id']
    
    def get_posts_count(self, obj):
        return Post.objects.filter(author=obj).count()

class UserUpdateSerializer(serializers.ModelSerializer):
    """프로필 수정 시리얼라이저"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
        if len(data['new_password']) < 8:
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")
        return data

class MyPostSerializer(serializers.ModelSerializer):
    """내 게시물 시리얼라이저"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_username', 'created_at', 'audio_file', 'image']
        read_only_fields = ['id', 'author', 'created_at']
