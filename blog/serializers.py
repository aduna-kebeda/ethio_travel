from rest_framework import serializers
from .models import BlogPost, BlogComment, SavedPost
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from bson import ObjectId
from rest_framework.exceptions import ValidationError
import uuid

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'tags',
            'imageUrl', 'author', 'authorName', 'authorImage',
            'status', 'views', 'readTime', 'featured',
            'createdAt', 'updatedAt'
        ]
        read_only_fields = ['slug', 'author', 'authorName', 'authorImage', 'views', 'readTime', 'createdAt', 'updatedAt']

    def create(self, validated_data):
        request = self.context.get('request')
        
        # Set author info
        validated_data['author'] = request.user
        validated_data['authorName'] = request.user.get_full_name() or request.user.username
        validated_data['authorImage'] = request.user.profile_image.url if hasattr(request.user, 'profile_image') else None
        
        # Generate unique slug
        base_slug = slugify(validated_data['title'])
        unique_id = str(uuid.uuid4())[:8]
        validated_data['slug'] = f"{base_slug}-{unique_id}"
        
        # Calculate read time
        word_count = len(validated_data.get('content', '').split())
        validated_data['readTime'] = f"{max(1, round(word_count / 200))} min read"
        
        # Set defaults
        validated_data['views'] = 0
        validated_data['featured'] = validated_data.get('featured', False)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update slug if title changes
        if 'title' in validated_data and validated_data['title'] != instance.title:
            base_slug = slugify(validated_data['title'])
            unique_id = str(uuid.uuid4())[:8]
            validated_data['slug'] = f"{base_slug}-{unique_id}"
        
        # Update read time if content changes
        if 'content' in validated_data:
            word_count = len(validated_data['content'].split())
            validated_data['readTime'] = f"{max(1, round(word_count / 200))} min read"
        
        return super().update(instance, validated_data)

class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'user', 'content', 'createdAt']
        read_only_fields = ['user', 'createdAt']

class SavedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'savedAt']
        read_only_fields = ['user', 'savedAt'] 