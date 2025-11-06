from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    postId = serializers.IntegerField(source='id', read_only=True)
    image = serializers.SerializerMethodField()
    audio_file = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['postId', 'title', 'content', 'author', 'created_at', 'audio_file', 'image']
        read_only_fields = ['author', 'created_at']
    
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
    
    def create(self, validated_data):       
        request = self.context.get('request')
        
        image_file = request.FILES.get('image', None)
        audio_file = request.FILES.get('audio_file', None)
       
        post = Post.objects.create(
            **validated_data,
            image=image_file,
            audio_file=audio_file
        )
        return post
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        request = self.context.get('request')
        if request and request.FILES.get('image'):
            instance.image = request.FILES.get('image')
        if request and request.FILES.get('audio_file'):
            instance.audio_file = request.FILES.get('audio_file')
        instance.save()
        return instance