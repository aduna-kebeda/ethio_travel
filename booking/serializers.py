from rest_framework import serializers
from django.contrib.auth import get_user_model
from business.serializers import BusinessListSerializer
from .models import Booking, Payment, BookingReview
from events.serializers import EventListSerializer
from packages.serializers import PackageListSerializer

User = get_user_model()

class BookingListSerializer(serializers.ModelSerializer):
    event = EventListSerializer(read_only=True)
    business = BusinessListSerializer(read_only=True)
    package = PackageListSerializer(read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_email', 'event', 'business', 'package',
            'status', 'number_of_people', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'created_at', 'updated_at']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'event', 'business', 'package', 'number_of_people',
            'special_requests', 'status'
        ]

    def validate(self, data):
        if ('event' in data and 'business' in data) or ('event' in data and 'package' in data) or ('business' in data and 'package' in data):
            raise serializers.ValidationError("Provide exactly one of event, business, or package.")
        if 'event' not in data and 'business' not in data and 'package' not in data:
            raise serializers.ValidationError("Must provide one of event, business, or package.")
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    booking_details = BookingListSerializer(source='booking', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_details', 'amount',
            'payment_method', 'status', 'transaction_id',
            'payment_details', 'created_at'
        ]
        read_only_fields = ['id', 'booking_details', 'created_at']

    def validate_booking(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You can only make payments for your own bookings.")
        return value

class BookingReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingReview
        fields = ['id', 'booking', 'rating', 'title', 'content', 'helpful', 'reported', 'created_at', 'updated_at']
        read_only_fields = ['id', 'helpful', 'reported', 'created_at', 'updated_at']

    def validate(self, data):
        if data['booking'].user != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own bookings.")
        if data['rating'] < 1 or data['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return data