"""
Event Management System - Serializers
Author: Akbari Prayag
GitHub: https://github.com/Akbari-Prayag/Event-Management-System

DRF serializers for API request/response handling.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review, EventInvitation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'bio', 'location', 'profile_picture', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'event', 'user', 'user_id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RSVPSerializer(serializers.ModelSerializer):
    """Serializer for RSVP model."""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'event', 'event_title', 'user', 'user_id', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    organizer = UserSerializer(read_only=True)
    organizer_id = serializers.IntegerField(write_only=True, required=False)
    rsvps_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    user_rsvp = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'organizer', 'organizer_id',
            'location', 'start_time', 'end_time', 'is_public',
            'rsvps_count', 'reviews_count', 'average_rating', 'user_rsvp',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']

    def get_rsvps_count(self, obj):
        return obj.rsvps.count()

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / reviews.count(), 2)
        return None

    def get_user_rsvp(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rsvp = obj.rsvps.filter(user=request.user).first()
            if rsvp:
                return RSVPSerializer(rsvp).data
        return None

    def create(self, validated_data):
        organizer_id = validated_data.pop('organizer_id', None)
        if organizer_id:
            validated_data['organizer'] = User.objects.get(id=organizer_id)
        else:
            validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class EventInvitationSerializer(serializers.ModelSerializer):
    """Serializer for EventInvitation model."""
    user = UserSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)

    class Meta:
        model = EventInvitation
        fields = ['id', 'event', 'user', 'invited_by', 'created_at']
        read_only_fields = ['invited_by', 'created_at']

    def create(self, validated_data):
        validated_data['invited_by'] = self.context['request'].user
        return super().create(validated_data)

