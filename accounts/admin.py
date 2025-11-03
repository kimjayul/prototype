from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'posts_count', 'music_count', 'favorites_count', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at', 'posts_count', 'music_count', 'favorites_count']
    
    fieldsets = (
        ('사용자 정보', {
            'fields': ('user',)
        }),
        ('프로필 정보', {
            'fields': ('bio', 'profile_image')
        }),
        ('통계', {
            'fields': ('posts_count', 'music_count', 'favorites_count')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at')
        }),
    )
