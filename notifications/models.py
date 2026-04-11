"""
Notifications app — in-app notification system.
"""

from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIF_TYPES = [
        ('follow_request',  'Follow Request'),
        ('follow_accepted', 'Follow Request Accepted'),
        ('chat_request',    'Chat Request'),
        ('chat_accepted',   'Chat Request Accepted'),
        ('story_like',      'Story Like'),
        ('post_like',       'Post Like'),
        ('comment',         'Comment'),
    ]
    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_notifications')
    notif_type  = models.CharField(max_length=20, choices=NOTIF_TYPES)
    message     = models.CharField(max_length=255)
    url         = models.CharField(max_length=255, blank=True, default='')
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.notif_type}] → {self.recipient.username}: {self.message}'
