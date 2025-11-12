# posts/admin.py
from django.contrib import admin
from .models import Post, PostLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # ✅ likes_count만 남기고 나머지는 제거 (Post 모델에 필드가 없음)
    list_display = ['title', 'author', 'created_at', 'likes_count']
    list_filter = ['created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'author')
        }),
        ('미디어', {
            'fields': ('audio_file', 'image')
        }),
        # ✅ 통계 섹션 제거 (view_count, like_count 필드가 모델에 없음)
        ('메타데이터', {
            'fields': ('created_at',)
        }),
    )
    
    # ✅ likes_count를 메서드로 정의 (PostLike 모델과 연결)
    def likes_count(self, obj):
        """게시글의 좋아요 수를 반환"""
        return obj.postlike_set.count()
    
    likes_count.short_description = '좋아요 수'


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']
