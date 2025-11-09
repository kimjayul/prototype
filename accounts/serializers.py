from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Profile


# ==================== 기존 코드 (그대로 유지!) ====================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


# ==================== 여기서부터 새로 추가! ====================

class ProfileSerializer(serializers.ModelSerializer):
    """프로필 시리얼라이저"""
    class Meta:
        model = Profile
        fields = ['bio', 'profile_image']


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 시리얼라이저 (확장)"""
    bio = serializers.CharField(source='profile.bio', allow_blank=True, required=False)
    profile_image = serializers.ImageField(source='profile.profile_image', allow_null=True, required=False)
    posts_count = serializers.IntegerField(source='profile.posts_count', read_only=True)
    music_count = serializers.IntegerField(source='profile.music_count', read_only=True)
    favorites_count = serializers.IntegerField(source='profile.favorites_count', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'profile_image', 
                  'posts_count', 'music_count', 'favorites_count']
        read_only_fields = ['id']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        
        profile = instance.profile
        profile.bio = profile_data.get('bio', profile.bio)
        
        if 'profile_image' in profile_data:
            profile.profile_image = profile_data['profile_image']
        
        profile.save()
        
        return instance


class UserStatisticsSerializer(serializers.Serializer):
    """사용자 통계 시리얼라이저"""
    total_posts = serializers.IntegerField()
    total_music = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_favorites = serializers.IntegerField()


class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("기존 비밀번호가 일치하지 않습니다.")
        return value
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "새 비밀번호가 일치하지 않습니다."})
        
        validate_password(data['new_password'], self.context['request'].user)
        
        return data
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
