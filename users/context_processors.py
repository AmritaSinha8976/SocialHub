"""
Global template context — injected into every template.
Provides: active_theme, unread_notifications_count, pending_follow_requests_count
"""

from notifications.models import Notification
from users.models import FollowRequest


def global_context(request):
    ctx = {'active_theme': 'light'}
    if request.user.is_authenticated:
        ctx['active_theme'] = getattr(request.user.profile, 'theme', 'light')
        ctx['unread_notifications_count'] = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        ctx['pending_follow_requests_count'] = FollowRequest.objects.filter(
            receiver=request.user, status='pending'
        ).count()
    return ctx
