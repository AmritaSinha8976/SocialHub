"""
Users app models — Profile, Follow, FollowRequest, OTPVerification, Block
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import random, string
from django.utils import timezone
from datetime import timedelta


def _otp_expiry():
    return timezone.now() + timedelta(minutes=10)


class OTPVerification(models.Model):
    """
    Stores a 6-digit OTP sent to an email during registration.
    Expires in 10 minutes.
    """
    email       = models.EmailField(unique=True)
    otp         = models.CharField(max_length=6)
    first_name  = models.CharField(max_length=30, blank=True)
    last_name   = models.CharField(max_length=30, blank=True)
    username    = models.CharField(max_length=150)
    expires_at  = models.DateTimeField(default=_otp_expiry)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f'OTP for {self.email} ({self.otp})'


class Profile(models.Model):
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio             = models.TextField(max_length=500, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)
    website         = models.URLField(max_length=200, blank=True, default='')
    location        = models.CharField(max_length=100, blank=True, default='')
    is_private      = models.BooleanField(default=False)
    theme           = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'username': self.user.username})

    @property
    def followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    @property
    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()

    @property
    def posts_count(self):
        return self.user.posts.count()

    def can_view_posts(self, viewer):
        if not self.is_private:
            return True
        if not viewer or not viewer.is_authenticated:
            return False
        if viewer == self.user:
            return True
        return Follow.objects.filter(follower=viewer, following=self.user).exists()


class Follow(models.Model):
    follower   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower.username} → {self.following.username}'


class FollowRequest(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')]
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    receiver   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username} ({self.status})'


class Block(models.Model):
    """User A blocks User B — B cannot see A's content or interact."""
    blocker    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.blocker.username} blocked {self.blocked.username}'

    @classmethod
    def is_blocked(cls, user_a, user_b):
        """Returns True if either user has blocked the other."""
        return cls.objects.filter(
            models.Q(blocker=user_a, blocked=user_b) |
            models.Q(blocker=user_b, blocked=user_a)
        ).exists()
