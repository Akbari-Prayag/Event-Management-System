from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, RSVP, Review


@shared_task
def send_event_update_email(event_id):
    """Send email notification to all users who RSVP'd to an event when it's updated."""
    try:
        event = Event.objects.get(id=event_id)
        rsvps = RSVP.objects.filter(event=event)
        
        recipient_list = [rsvp.user.email for rsvp in rsvps if rsvp.user.email]
        
        if recipient_list:
            subject = f'Event Update: {event.title}'
            message = f'''
Hi there,

The event "{event.title}" has been updated.

Event Details:
- Title: {event.title}
- Location: {event.location}
- Start Time: {event.start_time}
- End Time: {event.end_time}

Please visit the event page to see the updated details.

Best regards,
Event Management System
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            
        return f'Email sent to {len(recipient_list)} recipients for event {event_id}'
    except Event.DoesNotExist:
        return f'Event {event_id} not found'


@shared_task
def send_new_event_email(event_id):
    """Send email notification when a new event is created (to invited users)."""
    try:
        event = Event.objects.get(id=event_id)
        
        # Send to invited users for private events
        from .models import EventInvitation
        invitations = EventInvitation.objects.filter(event=event)
        recipient_list = [inv.user.email for inv in invitations if inv.user.email]
        
        # For public events, you might want to send to all users or a mailing list
        # For now, we'll just send to invited users
        
        if recipient_list:
            subject = f'New Event: {event.title}'
            message = f'''
Hi there,

You've been invited to a new event: "{event.title}"

Event Details:
- Description: {event.description}
- Location: {event.location}
- Start Time: {event.start_time}
- End Time: {event.end_time}
- Organizer: {event.organizer.username}

We hope to see you there!

Best regards,
Event Management System
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            
        return f'Email sent to {len(recipient_list)} recipients for new event {event_id}'
    except Event.DoesNotExist:
        return f'Event {event_id} not found'


@shared_task
def send_rsvp_email(rsvp_id):
    """Send email notification when someone RSVPs to an event."""
    try:
        rsvp = RSVP.objects.select_related('event', 'user').get(id=rsvp_id)
        event = rsvp.event
        
        # Send email to the organizer
        if event.organizer.email:
            subject = f'New RSVP: {rsvp.user.username} - {event.title}'
            message = f'''
Hi {event.organizer.username},

{rsvp.user.username} has RSVP'd "{rsvp.status}" to your event "{event.title}".

Current RSVP count: {event.rsvps.count()}

Best regards,
Event Management System
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [event.organizer.email],
                fail_silently=False,
            )
            
        return f'RSVP email sent for RSVP {rsvp_id}'
    except RSVP.DoesNotExist:
        return f'RSVP {rsvp_id} not found'


@shared_task
def send_review_notification_email(review_id):
    """Send email notification when a review is posted."""
    try:
        review = Review.objects.select_related('event', 'user').get(id=review_id)
        event = review.event
        
        # Send email to the organizer
        if event.organizer.email:
            subject = f'New Review: {event.title}'
            message = f'''
Hi {event.organizer.username},

{review.user.username} has left a {review.rating}-star review for your event "{event.title}".

Comment: {review.comment}

Best regards,
Event Management System
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [event.organizer.email],
                fail_silently=False,
            )
            
        return f'Review notification email sent for review {review_id}'
    except Review.DoesNotExist:
        return f'Review {review_id} not found'

