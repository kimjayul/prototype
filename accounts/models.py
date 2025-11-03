from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """사용자 프로필 확장 모델"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="사용자")
    bio = models.TextField(blank=True, null=True, verbose_name="자기소개")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="프로필 이미지")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        verbose_name = "프로필"
        verbose_name_plural = "프로필들"
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def posts_count(self):
        """작성한 게시물 수"""
        return self.user.post_set.count()
    
    @property
    def music_count(self):
        """작성한 음악 수"""
        return self.user.music_works.count()
    
    @property
    def favorites_count(self):
        """좋아요한 게시물 + 음악 수"""
        return self.user.post_likes.count() + self.user.music_likes.count()


# Signal: User 생성 시 자동으로 Profile 생성
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
