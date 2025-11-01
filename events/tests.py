from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Event, RSVP, Review, UserProfile, EventInvitation


class EventAPITestCase(TestCase):
    """Test cases for Event API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123'
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create events
        self.public_event = Event.objects.create(
            title='Public Event',
            description='This is a public event',
            organizer=self.organizer,
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            is_public=True
        )
        
        self.private_event = Event.objects.create(
            title='Private Event',
            description='This is a private event',
            organizer=self.organizer,
            location='Private Location',
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=2),
            is_public=False
        )

    def get_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_list_public_events_unauthenticated(self):
        """Test that unauthenticated users can see public events."""
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Public Event')

    def test_list_events_authenticated(self):
        """Test that authenticated users can see public events."""
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see public event
        event_titles = [event['title'] for event in response.data['results']]
        self.assertIn('Public Event', event_titles)

    def test_create_event_unauthenticated(self):
        """Test that unauthenticated users cannot create events."""
        data = {
            'title': 'New Event',
            'description': 'Test description',
            'location': 'Test Location',
            'start_time': '2024-12-31T10:00:00Z',
            'end_time': '2024-12-31T12:00:00Z',
            'is_public': True
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_event_authenticated(self):
        """Test that authenticated users can create events."""
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'title': 'New Event',
            'description': 'Test description',
            'location': 'Test Location',
            'start_time': '2024-12-31T10:00:00Z',
            'end_time': '2024-12-31T12:00:00Z',
            'is_public': True
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Event')
        self.assertEqual(response.data['organizer']['username'], 'user1')

    def test_update_event_as_organizer(self):
        """Test that organizer can update their event."""
        token = self.get_token(self.organizer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'title': 'Updated Event Title'}
        response = self.client.patch(f'/api/events/{self.public_event.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Event Title')

    def test_update_event_as_non_organizer(self):
        """Test that non-organizers cannot update events."""
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'title': 'Unauthorized Update'}
        response = self.client.patch(f'/api/events/{self.public_event.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_as_organizer(self):
        """Test that organizer can delete their event."""
        token = self.get_token(self.organizer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/events/{self.public_event.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.public_event.id).exists())

    def test_private_event_access_unauthenticated(self):
        """Test that unauthenticated users cannot access private events."""
        response = self.client.get(f'/api/events/{self.private_event.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_private_event_access_invited_user(self):
        """Test that invited users can access private events."""
        # Invite user1 to private event
        EventInvitation.objects.create(
            event=self.private_event,
            user=self.user1,
            invited_by=self.organizer
        )
        
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/events/{self.private_event.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Private Event')

    def test_search_events(self):
        """Test event search functionality."""
        response = self.client.get('/api/events/?search=Public')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Public Event')

    def test_filter_events_by_location(self):
        """Test event filtering by location."""
        response = self.client.get('/api/events/?location=Test Location')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class RSVPAPITestCase(TestCase):
    """Test cases for RSVP API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123'
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.organizer,
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            is_public=True
        )

    def get_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_rsvp(self):
        """Test creating an RSVP."""
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'status': 'Going'}
        response = self.client.post(f'/api/events/{self.event.id}/rsvp/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'Going')
        self.assertTrue(RSVP.objects.filter(event=self.event, user=self.user1).exists())

    def test_update_rsvp(self):
        """Test updating an RSVP."""
        rsvp = RSVP.objects.create(event=self.event, user=self.user1, status='Going')
        
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'status': 'Maybe'}
        response = self.client.patch(f'/api/events/{self.event.id}/rsvp/{self.user1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Maybe')

    def test_update_rsvp_unauthorized(self):
        """Test that users cannot update other users' RSVPs."""
        user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        rsvp = RSVP.objects.create(event=self.event, user=self.user1, status='Going')
        
        token = self.get_token(user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'status': 'Not Going'}
        response = self.client.patch(f'/api/events/{self.event.id}/rsvp/{self.user1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReviewAPITestCase(TestCase):
    """Test cases for Review API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123'
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.organizer,
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            is_public=True
        )

    def get_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_review(self):
        """Test creating a review."""
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'rating': 5,
            'comment': 'Great event!'
        }
        response = self.client.post(f'/api/events/{self.event.id}/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertTrue(Review.objects.filter(event=self.event, user=self.user1).exists())

    def test_list_reviews(self):
        """Test listing reviews for an event."""
        Review.objects.create(
            event=self.event,
            user=self.user1,
            rating=5,
            comment='Great event!'
        )
        
        response = self.client.get(f'/api/events/{self.event.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], 5)

    def test_review_rating_validation(self):
        """Test that rating must be between 1 and 5."""
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'rating': 6,  # Invalid rating
            'comment': 'Test'
        }
        response = self.client.post(f'/api/events/{self.event.id}/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

