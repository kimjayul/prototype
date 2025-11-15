from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    like_count = models.IntegerField(default=0, verbose_name="좋아요 수")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.title)
    
    @property
    def likes_count(self):
        """좋아요 개수"""
        return self.post_likes.count()


class PostLike(models.Model):
    """게시물 좋아요 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name="사용자")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes', verbose_name="게시물")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 날짜")
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        verbose_name = "게시물 좋아요"
        verbose_name_plural = "게시물 좋아요들"
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"