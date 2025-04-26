from rest_framework import serializers
from .models import Destination, DestinationReview, SavedDestination
from users.serializers import UserSerializer

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = [
            'id', 'user', 'title', 'slug', 'description', 'category', 'region',
            'city', 'address', 'latitude', 'longitude', 'featured', 'status',
            'rating', 'review_count', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'slug', 'rating', 'review_count', 'created_at', 'updated_at']
    
    def validate(self, data):
        if 'latitude' in data and not -90 <= float(data['latitude']) <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        if 'longitude' in data and not -180 <= float(data['longitude']) <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return data

class DestinationDetailSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Destination
        fields = [
            'id', 'user', 'title', 'slug', 'description', 'category', 'region',
            'city', 'address', 'latitude', 'longitude', 'featured', 'status',
            'rating', 'review_count', 'images', 'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'slug', 'rating', 'review_count', 'created_at', 'updated_at']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:5]  # Latest 5 reviews
        return DestinationReviewSerializer(reviews, many=True).data

class DestinationReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DestinationReview
        fields = [
            'id', 'destination', 'user', 'rating', 'title', 'content',
            'helpful', 'reported', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'helpful', 'reported', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SavedDestinationSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    
    class Meta:
        model = SavedDestination
        fields = ['id', 'user', 'destination', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)