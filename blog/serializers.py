from rest_framework import serializers
from .models import BlogPost, BlogComment, SavedPost
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields

class BlogPostSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'tags', 'imageUrl',
            'author', 'author_details', 'authorName', 'authorImage',
            'status', 'views', 'readTime', 'featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'views', 'author_details',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'author': {'write_only': True, 'required': False},
            'authorName': {'required': False},
            'authorImage': {'required': False, 'allow_null': True},
            'status': {'default': 'draft'},
            'featured': {'default': False},
            'readTime': {'required': False, 'default': 5}
        }

    def create(self, validated_data):
        # Generate base slug
        base_slug = slugify(validated_data['title'])
        validated_data['slug'] = base_slug
        
        # Check if slug exists and append timestamp if it does
        if BlogPost.objects.filter(slug=base_slug).exists():
            timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
            validated_data['slug'] = f"{base_slug}-{timestamp}"
        
        # Set author if not provided
        if 'author' not in validated_data:
            validated_data['author'] = self.context['request'].user
        
        # Set authorName if not provided
        if 'authorName' not in validated_data:
            user = validated_data.get('author')
            if user:
                validated_data['authorName'] = user.get_full_name() or user.username
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        return super().update(instance, validated_data)

class BlogCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_details = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'post_details', 'user', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'post': {'write_only': True}
        }

    def get_post_details(self, obj):
        return {
            'title': obj.post.title,
            'slug': obj.post.slug
        }

class SavedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_details = serializers.SerializerMethodField()

    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'post_details', 'saved_at']
        read_only_fields = ['user', 'saved_at']
        extra_kwargs = {
            'post': {'write_only': True}
        }

    def get_post_details(self, obj):
        return {
            'title': obj.post.title,
            'slug': obj.post.slug,
            'imageUrl': obj.post.imageUrl
        }