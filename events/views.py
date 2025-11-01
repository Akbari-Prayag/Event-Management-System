from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Event, RSVP, Review, EventInvitation
from .serializers import (
    EventSerializer, RSVPSerializer, ReviewSerializer, EventInvitationSerializer
)
from .permissions import IsOrganizerOrReadOnly, IsPrivateEventAllowed, IsRSVPOwnerOrReadOnly
from .tasks import send_event_update_email, send_new_event_email, send_rsvp_email, send_review_notification_email


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing events.
    
    list: Returns a paginated list of public events (or private events user has access to)
    retrieve: Get details of a specific event
    create: Create a new event (authenticated users only)
    update: Update an event (only the organizer)
    destroy: Delete an event (only the organizer)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['organizer', 'location', 'is_public']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    ordering_fields = ['created_at', 'start_time', 'title']
    ordering = ['-created_at']
    permission_classes = [IsPrivateEventAllowed]

    def get_queryset(self):
        """
        Filter events based on user permissions.
        Public events are visible to all, private events only to authorized users.
        """
        queryset = Event.objects.all()
        
        if self.request.user.is_authenticated:
            # Show public events + private events user has access to
            from .models import EventInvitation
            user_invited_events = EventInvitation.objects.filter(
                user=self.request.user
            ).values_list('event_id', flat=True)
            user_rsvp_events = RSVP.objects.filter(
                user=self.request.user
            ).values_list('event_id', flat=True)
            
            queryset = Event.objects.filter(
                models.Q(is_public=True) |
                models.Q(organizer=self.request.user) |
                models.Q(id__in=user_invited_events) |
                models.Q(id__in=user_rsvp_events)
            ).distinct()
        else:
            # Non-authenticated users only see public events
            queryset = Event.objects.filter(is_public=True)
        
        return queryset

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]
        else:
            permission_classes = [AllowAny]
        
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create event and send notification emails to invited users."""
        event = serializer.save(organizer=self.request.user)
        
        # Send email notification for new event (async)
        send_new_event_email.delay(event.id)

    def perform_update(self, serializer):
        """Update event and notify RSVP'd users."""
        event = serializer.save()
        
        # Send email notification to RSVP'd users (async)
        send_event_update_email.delay(event.id)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        """Create or update RSVP for an event."""
        event = self.get_object()
        user = request.user
        
        # Check if RSVP already exists
        rsvp, created = RSVP.objects.get_or_create(
            event=event,
            user=user,
            defaults={'status': request.data.get('status', 'Going')}
        )
        
        if not created:
            # Update existing RSVP
            rsvp.status = request.data.get('status', rsvp.status)
            rsvp.save()
        
        # Send email notification (async)
        send_rsvp_email.delay(rsvp.id)
        
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='rsvp/(?P<user_id>[^/.]+)', permission_classes=[IsAuthenticated])
    def update_rsvp(self, request, pk=None, user_id=None):
        """Update RSVP status for a specific user."""
        event = self.get_object()
        
        # Only allow users to update their own RSVP, or organizers can update any RSVP
        if int(user_id) != request.user.id and event.organizer != request.user:
            return Response(
                {'detail': 'You do not have permission to update this RSVP.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rsvp = get_object_or_404(RSVP, event=event, user_id=user_id)
        rsvp.status = request.data.get('status', rsvp.status)
        rsvp.save()
        
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'get'], permission_classes=[AllowAny])
    def reviews(self, request, pk=None):
        """Add a review for an event (POST) or list all reviews (GET)."""
        event = self.get_object()
        
        if request.method == 'POST':
            # POST: Add a review (requires authentication)
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Authentication credentials were not provided.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check if user already reviewed this event
            review, created = Review.objects.get_or_create(
                event=event,
                user=request.user,
                defaults={
                    'rating': request.data.get('rating'),
                    'comment': request.data.get('comment', '')
                }
            )
            
            if not created:
                # Update existing review
                review.rating = request.data.get('rating', review.rating)
                review.comment = request.data.get('comment', review.comment)
                review.save()
            
            # Send email notification to organizer (async)
            send_review_notification_email.delay(review.id)
            
            serializer = ReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        else:  # GET
            # GET: List all reviews for an event
            reviews = event.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizerOrReadOnly])
    def invite_user(self, request, pk=None):
        """Invite a user to a private event (organizer only)."""
        event = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'detail': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth.models import User
        try:
            invited_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        invitation, created = EventInvitation.objects.get_or_create(
            event=event,
            user=invited_user,
            invited_by=request.user
        )
        
        serializer = EventInvitationSerializer(invitation)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

