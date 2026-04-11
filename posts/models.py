"""
Posts app models — Post, Like, Comment, SavedPost
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image      = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)
    caption    = models.TextField(max_length=2200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.caption[:50]}'

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'pk': self.pk})

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False

    def is_saved_by(self, user):
        if user.is_authenticated:
            return self.saved_by.filter(user=user).exists()
        return False


class Like(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} liked Post #{self.post.pk}'


class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text       = models.TextField(max_length=1000)
    parent     = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on Post #{self.post.pk}: {self.text[:50]}'

    @property
    def is_reply(self):
        return self.parent is not None


class SavedPost(models.Model):
    """Bookmarked / saved posts per user."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} saved Post #{self.post.pk}'
