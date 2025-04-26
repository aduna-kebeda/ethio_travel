from rest_framework import serializers
from .models import Business, BusinessReview, SavedBusiness
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BusinessReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = BusinessReview
        fields = ['id', 'user', 'rating', 'comment', 'helpful_votes', 
                 'is_reported', 'report_reason', 'created_at', 'updated_at']
        read_only_fields = ['user', 'helpful_votes', 'is_reported', 'report_reason']

class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'id', 'name', 'slug', 'business_type', 'description',
            'contact_email', 'contact_phone', 'website', 'region', 'city',
            'address', 'latitude', 'longitude', 'main_image', 'gallery_images',
            'social_media_links', 'opening_hours', 'facilities', 'services',
            'team', 'status', 'is_verified', 'is_featured', 'verification_date',
            'average_rating', 'total_reviews', 'created_at', 'updated_at'
        ]

class BusinessDetailSerializer(serializers.ModelSerializer):
    reviews = BusinessReviewSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'slug', 'business_type', 'description',
                 'contact_email', 'contact_phone', 'website', 'region', 'city',
                 'address', 'latitude', 'longitude', 'main_image', 'gallery_images',
                 'social_media_links', 'opening_hours', 'facilities', 'services',
                 'team', 'status', 'is_verified', 'is_featured', 'verification_date',
                 'average_rating', 'total_reviews', 'additional_data', 'created_at',
                 'updated_at', 'owner', 'reviews']
        read_only_fields = ['slug', 'status', 'is_verified', 'is_featured',
                           'verification_date', 'average_rating', 'total_reviews']

class BusinessCreateSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='name', required=True)
    phone = serializers.CharField(source='contact_phone', required=True)
    email = serializers.CharField(source='contact_email', required=True)
    image = serializers.URLField(source='main_image', required=False)
    coordinates = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
        write_only=True,
        required=False
    )
    social_media_links = serializers.JSONField(required=False)
    
    class Meta:
        model = Business
        fields = [
            'business_name', 'business_type', 'description',
            'email', 'phone', 'website', 'region', 'city', 'address',
            'coordinates', 'image', 'gallery_images', 'opening_hours',
            'facilities', 'services', 'team', 'social_media_links'
        ]
        extra_kwargs = {
            'business_type': {'required': True},
            'region': {'required': True},
            'city': {'required': True},
            'address': {'required': True},
        }

    def validate(self, data):
        # Validate coordinates if provided
        if 'coordinates' in data:
            coords = data['coordinates']
            if len(coords) != 2:
                raise serializers.ValidationError("Coordinates must be an array of [longitude, latitude]")
            
        return data

    def create(self, validated_data):
        # Handle coordinates
        coordinates = validated_data.pop('coordinates', None)
        if coordinates:
            validated_data['longitude'] = coordinates[0]
            validated_data['latitude'] = coordinates[1]
        
        # Set owner from request context
        validated_data['owner'] = self.context['request'].user
        
        # Create the business
        business = super().create(validated_data)
        
        return business

class SavedBusinessSerializer(serializers.ModelSerializer):
    business = BusinessListSerializer(read_only=True)
    
    class Meta:
        model = SavedBusiness
        fields = ['id', 'business', 'saved_at']
        read_only_fields = ['saved_at']

class BusinessReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessReview
        fields = ['rating', 'comment']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['business'] = self.context['business']
        return super().create(validated_data)