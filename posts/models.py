from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True) # ⭐️ image 필드 확인
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    like_count = models.IntegerField(default=0, verbose_name="좋아요 수")

    def __str__(self):
        return str(self.title)

