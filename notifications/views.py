from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notifications_list_view(request):
    notifs = Notification.objects.filter(
        recipient=request.user
    ).select_related('actor', 'actor__profile').order_by('-created_at')[:50]

    # Mark all as read
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'notifications/list.html', {'notifications': notifs})


@login_required
def mark_read_view(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect(notif.url or 'notifications:list')


@login_required
def unread_count_view(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})
