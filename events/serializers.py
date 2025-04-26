from rest_framework import serializers
from .models import Event, EventReview, EventRegistration, SavedEvent, EventSubscription
from users.serializers import UserSerializer

class EventReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventReview
        fields = [
            'id', 'event', 'user', 'rating', 'title', 'content',
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

class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'category', 'location', 'start_date',
            'end_date', 'featured', 'status', 'current_attendees', 'rating'
        ]
        read_only_fields = ['id', 'slug', 'status', 'current_attendees', 'rating']

class EventDetailSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()
    registration_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'category', 'start_date',
            'end_date', 'location', 'address', 'latitude', 'longitude',
            'featured', 'status', 'organizer', 'price', 'capacity',
            'current_attendees', 'rating', 'images', 'reviews',
            'registration_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'current_attendees', 'rating', 'created_at', 'updated_at']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:5]
        return EventReviewSerializer(reviews, many=True).data
    
    def get_registration_count(self, obj):
        return obj.registrations.count()

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'start_date',
            'end_date', 'location', 'address', 'latitude', 'longitude',
            'featured', 'status', 'organizer', 'price', 'capacity',
            'current_attendees', 'rating', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'current_attendees', 'rating', 'created_at', 'updated_at']
    
    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        if 'latitude' in data and data['latitude'] is not None and not -90 <= float(data['latitude']) <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        if 'longitude' in data and data['longitude'] is not None and not -180 <= float(data['longitude']) <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return data

class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SavedEventSerializer(serializers.ModelSerializer):
    event = EventListSerializer(read_only=True)
    
    class Meta:
        model = SavedEvent
        fields = ['id', 'user', 'event', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class EventSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSubscription
        fields = ['id', 'email', 'categories', 'created_at']
        read_only_fields = ['id', 'created_at']