from django.contrib import admin
from .models import Music, MusicLike


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'created_at', 'likes_count']
    list_filter = ['genre', 'created_at']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'author', 'genre')
        }),
        ('파일', {
            'fields': ('audio_file', 'cover_image')
        }),
        ('메타데이터', {
            'fields': ('duration', 'created_at', 'updated_at')
        }),
    )


@admin.register(MusicLike)
class MusicLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'music', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'music__title']
    readonly_fields = ['created_at']
