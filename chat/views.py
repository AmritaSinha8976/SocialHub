"""
Chat app views — request-gated one-to-one messaging.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q

from .models import ChatRequest, ChatRoom, Message
from .forms import MessageForm
from notifications.models import Notification


@login_required
def inbox_view(request):
    """Show all chat rooms the user is part of."""
    rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).prefetch_related('messages').order_by('-created_at')

    # Pending incoming chat requests
    pending_requests = ChatRequest.objects.filter(
        receiver=request.user, status='pending'
    ).select_related('sender', 'sender__profile')

    rooms_with_data = []
    for room in rooms:
        other  = room.get_other_user(request.user)
        last   = room.messages.last()
        unread = room.messages.filter(is_read=False).exclude(sender=request.user).count()
        rooms_with_data.append({'room': room, 'other': other, 'last': last, 'unread': unread})

    return render(request, 'chat/inbox.html', {
        'rooms_with_data': rooms_with_data,
        'pending_requests': pending_requests,
    })


@login_required
def send_chat_request_view(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('users:profile', username=username)

    # Check if a room already exists
    existing_room = ChatRoom.objects.filter(
        Q(user1=request.user, user2=target) | Q(user1=target, user2=request.user)
    ).first()
    if existing_room:
        return redirect('chat:room', room_id=existing_room.pk)

    req, created = ChatRequest.objects.get_or_create(
        sender=request.user, receiver=target,
        defaults={'status': 'pending'}
    )
    if created:
        Notification.objects.create(
            recipient=target,
            actor=request.user,
            notif_type='chat_request',
            message=f'{request.user.username} wants to chat with you.',
            url='/chat/',
        )
    return redirect('users:profile', username=username)


@login_required
def handle_chat_request_view(request, request_id, action):
    creq = get_object_or_404(ChatRequest, pk=request_id, receiver=request.user, status='pending')
    if action == 'accept':
        creq.status = 'accepted'
        creq.save()
        room = ChatRoom.get_or_create_for(creq.sender, creq.receiver)
        Notification.objects.create(
            recipient=creq.sender,
            actor=request.user,
            notif_type='chat_accepted',
            message=f'{request.user.username} accepted your chat request.',
            url=f'/chat/{room.pk}/',
        )
        return redirect('chat:room', room_id=room.pk)
    else:
        creq.status = 'rejected'
        creq.save()
    return redirect('chat:inbox')


@login_required
def chat_room_view(request, room_id):
    room = get_object_or_404(ChatRoom, pk=room_id)
    if request.user not in (room.user1, room.user2):
        return redirect('chat:inbox')

    other = room.get_other_user(request.user)

    # Mark messages as read
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.room   = room
            msg.sender = request.user
            msg.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': msg.pk,
                    'text': msg.text,
                    'sender': msg.sender.username,
                    'created_at': msg.created_at.strftime('%H:%M'),
                    'is_mine': True,
                })
        return redirect('chat:room', room_id=room_id)

    messages_qs = room.messages.select_related('sender').all()
    form = MessageForm()

    # Poll endpoint: return new messages after a given id
    after = request.GET.get('after')
    if after and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_msgs = messages_qs.filter(pk__gt=after)
        return JsonResponse({'messages': [
            {
                'id': m.pk,
                'text': m.text,
                'sender': m.sender.username,
                'created_at': m.created_at.strftime('%H:%M'),
                'is_mine': m.sender == request.user,
            } for m in new_msgs
        ]})

    return render(request, 'chat/room.html', {
        'room': room, 'other': other, 'messages': messages_qs, 'form': form,
    })
