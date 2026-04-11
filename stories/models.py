"""
Stories app models — full Instagram-like story with stickers, text layers, music metadata.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


def story_expires_at():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    FILTER_CHOICES = [
        ('none',       'None'),
        ('clarendon',  'Clarendon'),
        ('gingham',    'Gingham'),
        ('moon',       'Moon'),
        ('lark',       'Lark'),
        ('reyes',      'Reyes'),
        ('juno',       'Juno'),
        ('slumber',    'Slumber'),
        ('crema',      'Crema'),
    ]

    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    image       = models.ImageField(upload_to='stories/%Y/%m/%d/', blank=True, null=True)

    # Text overlay
    caption     = models.CharField(max_length=300, blank=True, default='')
    text_color  = models.CharField(max_length=7,  default='#FFFFFF')
    text_size   = models.IntegerField(default=24)                        # px
    text_align  = models.CharField(max_length=10, default='center',
                                   choices=[('left','Left'),('center','Center'),('right','Right')])
    text_style  = models.CharField(max_length=20, default='normal',
                                   choices=[('normal','Normal'),('bold','Bold'),('italic','Italic'),('shadow','Shadow'),('neon','Neon')])

    # Background (when no image)
    bg_color    = models.CharField(max_length=7,  default='#000000')
    bg_gradient = models.CharField(max_length=100, blank=True, default='')  # e.g. "135deg,#f093fb,#f5576c"

    # Filter
    filter_name = models.CharField(max_length=20, choices=FILTER_CHOICES, default='none')

    # Sticker / emoji overlay (JSON string: [{type,value,x,y,rotation,scale}])
    stickers_json = models.TextField(blank=True, default='[]')

    # Music metadata (decorative display only — no audio file stored)
    music_title  = models.CharField(max_length=100, blank=True, default='')
    music_artist = models.CharField(max_length=100, blank=True, default='')

    # Poll (optional)
    poll_question = models.CharField(max_length=120, blank=True, default='')
    poll_option_a = models.CharField(max_length=60,  blank=True, default='')
    poll_option_b = models.CharField(max_length=60,  blank=True, default='')

    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField(default=story_expires_at)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f'{self.author.username} story @ {self.created_at:%Y-%m-%d %H:%M}'

    @property
    def is_active(self):
        return timezone.now() < self.expires_at

    def has_been_viewed_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.views.filter(viewer=user).exists()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.story_likes.filter(user=user).exists()


class StoryPollVote(models.Model):
    story   = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='poll_votes')
    user    = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='poll_votes')
    choice  = models.CharField(max_length=1, choices=[('a','A'),('b','B')])

    class Meta:
        unique_together = ('story', 'user')

    def __str__(self):
        return f'{self.user.username} voted {self.choice} on story {self.story.pk}'


class StoryView(models.Model):
    story     = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewer    = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='story_views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'viewer')


class StoryLike(models.Model):
    story      = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_likes')
    user       = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='story_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'user')
