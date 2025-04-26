from rest_framework import serializers
from .models import Package, PackageReview, SavedPackage, Departure
from users.models import User

class PackageReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageReview
        fields = ['id', 'user', 'user_image', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'user_image', 'created_at']

    def get_user(self, obj):
        return obj.user.email

    def get_user_image(self, obj):
        return obj.user.image.url if hasattr(obj.user, 'image') and obj.user.image else None

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DepartureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departure
        fields = ['id', 'package', 'start_date', 'end_date', 'price', 'available_slots', 'is_guaranteed']
        read_only_fields = ['id']

class PackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'category', 'location', 'region',
            'price', 'discounted_price', 'duration', 'duration_in_days',
            'image', 'rating', 'featured'
        ]
        read_only_fields = ['id', 'slug', 'rating']

class PackageDetailSerializer(serializers.ModelSerializer):
    reviews = PackageReviewSerializer(many=True, read_only=True)
    departures = DepartureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'user', 'title', 'slug', 'description', 'short_description',
            'location', 'region', 'price', 'discounted_price', 'duration',
            'duration_in_days', 'image', 'gallery_images', 'category',
            'included', 'not_included', 'itinerary', 'departure',
            'departure_time', 'return_time', 'max_group_size', 'min_age',
            'difficulty', 'tour_guide', 'languages', 'rating', 'coordinates',
            'status', 'featured', 'created_at', 'updated_at', 'reviews',
            'departures'
        ]
        read_only_fields = ['id', 'user', 'slug', 'rating', 'created_at', 'updated_at']

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'id', 'user', 'title', 'slug', 'description', 'short_description',
            'location', 'region', 'price', 'discounted_price', 'duration',
            'duration_in_days', 'image', 'gallery_images', 'category',
            'included', 'not_included', 'itinerary', 'departure',
            'departure_time', 'return_time', 'max_group_size', 'min_age',
            'difficulty', 'tour_guide', 'languages', 'coordinates',
            'status', 'featured'
        ]
        read_only_fields = ['id', 'user', 'slug']

    def validate(self, data):
        if 'coordinates' in data and len(data['coordinates']) == 2:
            lat, lon = data['coordinates']
            if not -90 <= lat <= 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90")
            if not -180 <= lon <= 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180")
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SavedPackageSerializer(serializers.ModelSerializer):
    package = PackageListSerializer(read_only=True)
    
    class Meta:
        model = SavedPackage
        fields = ['id', 'package', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)