from django.db import models
from django.contrib.auth.models import User


class Music(models.Model):
    title = models.CharField(max_length=255, verbose_name="제목")
    description = models.TextField(blank=True, null=True, verbose_name="설명")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='music_works', verbose_name="작성자")
    artist = models.CharField(max_length=255, blank=True, null=True, verbose_name="아티스트명")  # ⭐ 추가!
    audio_file = models.FileField(upload_to='music/audio/', verbose_name="오디오 파일")
    cover_image = models.ImageField(upload_to='music/covers/', blank=True, null=True, verbose_name="커버 이미지")
    genre = models.CharField(max_length=100, blank=True, null=True, verbose_name="장르")
    duration = models.IntegerField(blank=True, null=True, verbose_name="재생 시간(초)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "음악"
        verbose_name_plural = "음악들"
    
    def __str__(self):
        return self.title
    
    @property
    def likes_count(self):
        """좋아요 개수"""
        return self.music_likes.count()


class MusicLike(models.Model):
    """음악 좋아요 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='music_likes', verbose_name="사용자")
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='music_likes', verbose_name="음악")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 날짜")
    
    class Meta:
        unique_together = ('user', 'music')  # 한 사용자가 같은 음악에 중복 좋아요 방지
        ordering = ['-created_at']
        verbose_name = "음악 좋아요"
        verbose_name_plural = "음악 좋아요들"
    
    def __str__(self):
        return f"{self.user.username} likes {self.music.title}"
