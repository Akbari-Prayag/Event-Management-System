from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review, EventInvitation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'location', 'created_at']
    search_fields = ['user__username', 'full_name', 'location']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'location', 'start_time', 'is_public', 'created_at']
    list_filter = ['is_public', 'start_time', 'created_at']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['event__title', 'user__username']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['event__title', 'user__username', 'comment']


@admin.register(EventInvitation)
class EventInvitationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'invited_by', 'created_at']
    search_fields = ['event__title', 'user__username', 'invited_by__username']

