from django import template
from users.models import Follow
from posts.models import Like, SavedPost

register = template.Library()


@register.filter
def is_liked_by(post, user):
    if not user or not user.is_authenticated:
        return False
    return Like.objects.filter(user=user, post=post).exists()


@register.filter
def is_saved_by(post, user):
    if not user or not user.is_authenticated:
        return False
    return SavedPost.objects.filter(user=user, post=post).exists()


@register.filter
def is_followed_by(target_user, current_user):
    if not current_user.is_authenticated:
        return False
    return Follow.objects.filter(follower=current_user, following=target_user).exists()


@register.filter
def profile_pic(user):
    try:
        return user.profile.profile_picture.url
    except Exception:
        return '/static/images/default_avatar.png'


@register.filter
def can_view_posts(profile, viewer):
    return profile.can_view_posts(viewer)
