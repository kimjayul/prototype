from django.contrib import admin
from .models import Post, PostLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'likes_count', 'view_count', 'like_count']
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
        ('통계', {
            'fields': ('view_count', 'like_count')
        }),
        ('메타데이터', {
            'fields': ('created_at',)
        }),
    )


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']
