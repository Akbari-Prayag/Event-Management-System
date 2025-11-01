from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers of an event to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the organizer of the event
        return obj.organizer == request.user


class IsPrivateEventAllowed(permissions.BasePermission):
    """
    Custom permission to allow access to private events only for:
    - The organizer
    - Invited users
    - Users who have RSVP'd
    """

    def has_object_permission(self, request, view, obj):
        # Public events are accessible to everyone
        if obj.is_public:
            return True

        # For private events, check if user is organizer
        if obj.organizer == request.user:
            return True

        # Check if user is invited
        from .models import EventInvitation
        if EventInvitation.objects.filter(event=obj, user=request.user).exists():
            return True

        # Check if user has RSVP'd (they may have been invited indirectly)
        if obj.rsvps.filter(user=request.user).exists():
            return True

        return False


class IsRSVPOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the RSVP owner to update their own RSVP.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the RSVP owner
        return obj.user == request.user

