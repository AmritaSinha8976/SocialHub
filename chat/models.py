"""
Chat app models — request-gated one-to-one messaging.
"""

from django.db import models
from django.contrib.auth.models import User


class ChatRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chat_requests')
    receiver   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chat_requests')
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f'ChatRequest {self.sender} → {self.receiver} [{self.status}]'


class ChatRoom(models.Model):
    """
    A private room between exactly two users, created when a ChatRequest is accepted.
    """
    user1      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_as_user1')
    user2      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f'Room({self.user1.username} ↔ {self.user2.username})'

    def get_other_user(self, user):
        return self.user2 if self.user1 == user else self.user1

    @classmethod
    def get_or_create_for(cls, user_a, user_b):
        """Always store the pair with lower pk first to maintain uniqueness."""
        u1, u2 = (user_a, user_b) if user_a.pk < user_b.pk else (user_b, user_a)
        room, created = cls.objects.get_or_create(user1=u1, user2=u2)
        return room


class Message(models.Model):
    room       = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text       = models.TextField(max_length=2000)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.text[:40]}'
