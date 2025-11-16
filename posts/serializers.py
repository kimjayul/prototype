class PostDetailSerializer(serializers.ModelSerializer):
    """게시물 상세 시리얼라이저 (MyPage용)"""
    author = PostAuthorSerializer(read_only=True)
    postId = serializers.IntegerField(source='id', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    audio_file = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'postId', 'title', 'content', 'author', 'audio_file', 'image',
                  'created_at', 'likes_count', 'is_liked', 'view_count', 'like_count']
        read_only_fields = ['id', 'created_at', 'author', 'view_count', 'like_count']
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_audio_file(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None
    
    def get_is_liked(self, obj):
        """현재 사용자가 좋아요 했는지 확인"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False
