from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Music, MusicLike


class MusicAuthorSerializer(serializers.ModelSerializer):
    """음악 작성자 정보 (간단 버전)"""
    class Meta:
        model = User
        fields = ['id', 'username']


class MusicSerializer(serializers.ModelSerializer):
    author = MusicAuthorSerializer(read_only=True)
    artist = serializers.CharField(allow_blank=True, required=False)  # ⭐ 추가!
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()  # 🆕 추가! (audio_file 별칭)
    
   class Meta:
        model = Music
        fields = ['id', 'title', 'description', 'author', 'artist',
                  'audio_file', 'file_url', 'cover_image', 'genre', 'duration',  # 🆕 file_url 추가!
                  'created_at', 'updated_at', 'likes_count', 'is_liked']  # 🆕 updated_at 추가!
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']  # 🆕 updated_at 추가!
    
    def get_is_liked(self, obj):
        """현재 사용자가 좋아요 했는지 확인"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return MusicLike.objects.filter(user=request.user, music=obj).exists()
        return False


class FavoriteMusicSerializer(serializers.ModelSerializer):
    """좋아요한 음악 시리얼라이저"""
    music = MusicSerializer(read_only=True)
    
    class Meta:
        model = MusicLike
        fields = ['id', 'music', 'created_at']
        read_only_fields = ['id', 'created_at']
