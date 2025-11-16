from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, PostLike


# ==================== 기존 PostSerializer (FINAL_BACKEND 유지!) ====================
class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    postId = serializers.IntegerField(source='id', read_only=True)
    image = serializers.SerializerMethodField()  # ✅ FINAL_BACKEND 기능 유지
    audio_file = serializers.SerializerMethodField()  # ✅ FINAL_BACKEND 기능 유지

    class Meta:
        model = Post
        fields = ['postId', 'title', 'content', 'author', 'created_at', 'audio_file', 'image',
                  'view_count', 'like_count']  # ✅ mypage에서 view_count, like_count 추가
        read_only_fields = ['author', 'created_at', 'view_count', 'like_count']
    
    # ✅ FINAL_BACKEND 기능 유지
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    # ✅ FINAL_BACKEND 기능 유지
    def get_audio_file(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None
    
    # ✅ 수정된 create 메서드
    def create(self, validated_data):
        request = self.context.get('request')
        
        # validated_data에서 image와 audio_file 제거 (중복 방지)
        validated_data.pop('image', None)
        validated_data.pop('audio_file', None)
        
        # FILES에서 파일 가져오기
        image_file = request.FILES.get('image', None)
        audio_file = request.FILES.get('audio_file', None)
        
        # Post 객체 생성
        post = Post.objects.create(
            **validated_data,
            image=image_file,
            audio_file=audio_file
        )
        return post
    
    # ✅ FINAL_BACKEND 기능 유지
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        request = self.context.get('request')
        if request and request.FILES.get('image'):
            instance.image = request.FILES.get('image')
        if request and request.FILES.get('audio_file'):
            instance.audio_file = request.FILES.get('audio_file')
        instance.save()
        return instance


# ==================== 여기서부터 mypage 새로 추가! ====================

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
    # ✅ 추가: SerializerMethodField로 변경
    image = serializers.SerializerMethodField()
    audio_file = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'audio_file', 'image',
                  'created_at', 'likes_count', 'is_liked', 'view_count', 'like_count']
        read_only_fields = ['id', 'created_at', 'author', 'view_count', 'like_count']
    
    # ✅ 추가: 완전한 URL 반환 메서드
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    # ✅ 추가: 완전한 URL 반환 메서드
    def get_audio_file(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None
    
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
