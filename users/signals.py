"""
Users app signals.
Automatically create/save a Profile whenever a User is created/saved.
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import DatabaseError


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile automatically when a new User is registered."""
    if created:
        # Import here to avoid circular imports and to survive mid-migration runs
        try:
            from .models import Profile
            Profile.objects.get_or_create(user=instance)
        except DatabaseError:
            # Table doesn't exist yet (e.g. during initial migrate) — skip silently
            pass


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the Profile whenever the User is saved."""
    try:
        from .models import Profile
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()
    except DatabaseError:
        pass
