"""
API Views — all endpoints for the React Native app.
"""

import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Profile, Follow, FollowRequest, Block, OTPVerification
from posts.models import Post, Like, Comment, SavedPost
from stories.models import Story, StoryView, StoryLike, StoryPollVote
from chat.models import ChatRequest, ChatRoom, Message
from notifications.models import Notification

from .serializers import (
    UserSerializer, UserMiniSerializer,
    OTPRequestSerializer, OTPVerifySerializer, SetPasswordSerializer,
    PostSerializer, CommentSerializer,
    StorySerializer,
    MessageSerializer, ChatRoomSerializer, ChatRequestSerializer,
    NotificationSerializer, FollowRequestSerializer,
)

from django.core.mail import send_mail
from django.conf import settings as django_settings


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


# ══ AUTH ══════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def api_otp_request(request):
    """Step 1: Send OTP to email."""
    ser = OTPRequestSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)

    d        = ser.validated_data
    otp_code = OTPVerification.generate_otp()

    OTPVerification.objects.filter(email=d['email']).delete()
    OTPVerification.objects.create(
        email      = d['email'],
        otp        = otp_code,
        username   = d['username'],
        first_name = d['first_name'],
        last_name  = d.get('last_name', ''),
        is_verified= False,
    )

    try:
        send_mail(
            subject='Your SocialHub OTP Code',
            message=f"Hi {d['first_name']},\n\nYour OTP is: {otp_code}\n\nExpires in 10 minutes.\n\n— SocialHub Team",
            from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'noreply@socialhub.com'),
            recipient_list=[d['email']],
            fail_silently=False,
        )
    except Exception:
        pass

    return Response({'message': f"OTP sent to {d['email']}"})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_otp_verify(request):
    """Step 2: Verify OTP."""
    ser = OTPVerifySerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)

    email = ser.validated_data['email']
    otp   = ser.validated_data['otp']

    try:
        record = OTPVerification.objects.get(email=email, is_verified=False)
    except OTPVerification.DoesNotExist:
        return Response({'error': 'OTP not found. Please request again.'}, status=400)

    if record.is_expired():
        return Response({'error': 'OTP expired. Please request a new one.'}, status=400)

    if record.otp != otp:
        return Response({'error': 'Incorrect OTP.'}, status=400)

    record.is_verified = True
    record.save()
    return Response({'message': 'OTP verified. Proceed to set password.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_set_password(request):
    """Step 3: Set password and create account. Returns JWT tokens."""
    ser = SetPasswordSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)

    email = ser.validated_data['email']
    try:
        record = OTPVerification.objects.get(email=email, is_verified=True)
    except OTPVerification.DoesNotExist:
        return Response({'error': 'Email not verified.'}, status=400)

    user = User.objects.create_user(
        username   = record.username,
        email      = record.email,
        password   = ser.validated_data['password'],
        first_name = record.first_name,
        last_name  = record.last_name,
    )
    record.delete()
    return Response({'tokens': get_tokens(user), 'user': UserSerializer(user, context={'request': request}).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Login with username + password. Returns JWT tokens."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    user     = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid username or password.'}, status=401)
    return Response({'tokens': get_tokens(user), 'user': UserSerializer(user, context={'request': request}).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Blacklist refresh token on logout."""
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Logged out.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    """Get current user's profile."""
    return Response(UserSerializer(request.user, context={'request': request}).data)


# ══ USERS ═════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def api_user_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    if request.user.is_authenticated and request.user != user:
        if Block.is_blocked(request.user, user):
            return Response({'error': 'User not available.'}, status=403)

    return Response(UserSerializer(user, context={'request': request}).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_edit_profile(request):
    profile = request.user.profile
    # Update user fields
    for field in ['first_name', 'last_name', 'email']:
        if field in request.data:
            setattr(request.user, field, request.data[field])
    request.user.save()

    # Update profile fields
    for field in ['bio', 'website', 'location', 'is_private', 'theme']:
        if field in request.data:
            setattr(profile, field, request.data[field])
    if 'profile_picture' in request.FILES:
        profile.profile_picture = request.FILES['profile_picture']
    profile.save()

    return Response(UserSerializer(request.user, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_theme(request):
    profile = request.user.profile
    profile.theme = 'dark' if profile.theme == 'light' else 'light'
    profile.save(update_fields=['theme'])
    return Response({'theme': profile.theme})


@api_view(['GET'])
@permission_classes([AllowAny])
def api_search_users(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response([])

    blocked_ids = []
    if request.user.is_authenticated:
        blocked_ids = list(Block.objects.filter(
            Q(blocker=request.user) | Q(blocked=request.user)
        ).values_list('blocker_id', 'blocked_id'))
        blocked_ids = list({uid for pair in blocked_ids for uid in pair})

    users = User.objects.filter(username__icontains=query).exclude(id__in=blocked_ids)
    if request.user.is_authenticated:
        users = users.exclude(id=request.user.id)
    return Response(UserMiniSerializer(users[:20], many=True, context={'request': request}).data)


# ══ FOLLOW ════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_follow(request, username):
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    if request.user == target:
        return Response({'error': 'Cannot follow yourself.'}, status=400)
    if Block.is_blocked(request.user, target):
        return Response({'error': 'Blocked.'}, status=403)

    target_profile, _ = Profile.objects.get_or_create(user=target)
    existing = Follow.objects.filter(follower=request.user, following=target)

    if existing.exists():
        existing.delete()
        FollowRequest.objects.filter(sender=request.user, receiver=target).delete()
        return Response({'is_following': False, 'follow_request_status': None,
                         'followers_count': Follow.objects.filter(following=target).count()})

    if target_profile.is_private:
        freq, created = FollowRequest.objects.get_or_create(
            sender=request.user, receiver=target, defaults={'status': 'pending'})
        if created:
            Notification.objects.create(
                recipient=target, actor=request.user, notif_type='follow_request',
                message=f'{request.user.username} sent you a follow request.',
                url='/follow-requests/',
            )
        return Response({'is_following': False, 'follow_request_status': freq.status,
                         'followers_count': Follow.objects.filter(following=target).count()})

    Follow.objects.get_or_create(follower=request.user, following=target)
    Notification.objects.create(
        recipient=target, actor=request.user, notif_type='follow_request',
        message=f'{request.user.username} started following you.',
        url=f'/profile/{request.user.username}/',
    )
    return Response({'is_following': True, 'follow_request_status': 'accepted',
                     'followers_count': Follow.objects.filter(following=target).count()})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_follow_requests(request):
    pending = FollowRequest.objects.filter(receiver=request.user, status='pending')\
                .select_related('sender', 'sender__profile')
    return Response(FollowRequestSerializer(pending, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_handle_follow_request(request, request_id, action):
    try:
        freq = FollowRequest.objects.get(pk=request_id, receiver=request.user, status='pending')
    except FollowRequest.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    if action == 'accept':
        freq.status = 'accepted'; freq.save()
        Follow.objects.get_or_create(follower=freq.sender, following=request.user)
        Notification.objects.create(
            recipient=freq.sender, actor=request.user, notif_type='follow_accepted',
            message=f'{request.user.username} accepted your follow request.',
            url=f'/profile/{request.user.username}/',
        )
    elif action == 'reject':
        freq.status = 'rejected'; freq.save()

    return Response({'status': freq.status})


# ══ BLOCK ═════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_block(request, username):
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    block = Block.objects.filter(blocker=request.user, blocked=target)
    if block.exists():
        block.delete()
        return Response({'is_blocked': False})
    Block.objects.create(blocker=request.user, blocked=target)
    Follow.objects.filter(
        Q(follower=request.user, following=target) | Q(follower=target, following=request.user)
    ).delete()
    return Response({'is_blocked': True})


# ══ POSTS ═════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_feed(request):
    following_ids = list(Follow.objects.filter(
        follower=request.user).values_list('following_id', flat=True))
    feed_ids = following_ids + [request.user.id]

    posts = Post.objects.filter(author_id__in=feed_ids)\
                .select_related('author', 'author__profile')\
                .prefetch_related('likes', 'comments')

    page  = int(request.GET.get('page', 1))
    size  = 10
    start = (page - 1) * size
    end   = start + size
    total = posts.count()

    return Response({
        'results':   PostSerializer(posts[start:end], many=True, context={'request': request}).data,
        'count':     total,
        'next':      page + 1 if end < total else None,
        'previous':  page - 1 if page > 1 else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_explore(request):
    posts = Post.objects.select_related('author', 'author__profile')\
                .prefetch_related('likes', 'comments').order_by('-created_at')

    if request.user.is_authenticated:
        following_ids = set(Follow.objects.filter(
            follower=request.user).values_list('following_id', flat=True))
        following_ids.add(request.user.id)
        posts = [p for p in posts if not p.author.profile.is_private or p.author_id in following_ids]
    else:
        posts = [p for p in posts if not p.author.profile.is_private]

    page  = int(request.GET.get('page', 1))
    size  = 12
    start = (page - 1) * size
    end   = start + size
    slice_ = posts[start:end]

    return Response({
        'results':  PostSerializer(slice_, many=True, context={'request': request}).data,
        'count':    len(posts),
        'next':     page + 1 if end < len(posts) else None,
        'previous': page - 1 if page > 1 else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_create_post(request):
    caption = request.data.get('caption', '').strip()
    image   = request.FILES.get('image')
    if not caption and not image:
        return Response({'error': 'Post needs an image or caption.'}, status=400)
    post = Post.objects.create(author=request.user, caption=caption, image=image)
    return Response(PostSerializer(post, context={'request': request}).data, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_post_detail(request, pk):
    try:
        post = Post.objects.select_related('author', 'author__profile').get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    if post.author.profile.is_private and request.user.is_authenticated:
        if request.user != post.author:
            if not Follow.objects.filter(follower=request.user, following=post.author).exists():
                return Response({'error': 'Private account.'}, status=403)

    comments = Comment.objects.filter(post=post, parent=None).select_related('author', 'author__profile')
    return Response({
        'post':     PostSerializer(post, context={'request': request}).data,
        'comments': CommentSerializer(comments, many=True, context={'request': request}).data,
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_post(request, pk):
    try:
        post = Post.objects.get(pk=pk, author=request.user)
    except Post.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    post.delete()
    return Response({'message': 'Post deleted.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_like(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    like = Like.objects.filter(user=request.user, post=post)
    if like.exists():
        like.delete(); is_liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        is_liked = True
        if post.author != request.user:
            Notification.objects.get_or_create(
                recipient=post.author, actor=request.user, notif_type='post_like',
                defaults={'message': f'{request.user.username} liked your post.', 'url': f'/post/{post.pk}/'},
            )
    return Response({'is_liked': is_liked, 'likes_count': post.likes_count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_save(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    saved = SavedPost.objects.filter(user=request.user, post=post)
    if saved.exists():
        saved.delete(); is_saved = False
    else:
        SavedPost.objects.create(user=request.user, post=post); is_saved = True
    return Response({'is_saved': is_saved})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_saved_posts(request):
    saved = SavedPost.objects.filter(user=request.user)\
                .select_related('post', 'post__author', 'post__author__profile')
    posts = [s.post for s in saved]
    return Response(PostSerializer(posts, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_comment(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    text = request.data.get('text', '').strip()
    if not text:
        return Response({'error': 'Comment cannot be empty.'}, status=400)

    comment = Comment.objects.create(post=post, author=request.user, text=text)
    if post.author != request.user:
        Notification.objects.create(
            recipient=post.author, actor=request.user, notif_type='comment',
            message=f'{request.user.username} commented on your post.',
            url=f'/post/{post.pk}/',
        )
    return Response(CommentSerializer(comment, context={'request': request}).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_comment(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    if request.user not in (comment.author, comment.post.author):
        return Response({'error': 'Not allowed.'}, status=403)
    comment.delete()
    return Response({'message': 'Comment deleted.'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_user_posts(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.can_view_posts(request.user):
        return Response({'error': 'Private account.'}, status=403)

    posts = user.posts.all()
    return Response(PostSerializer(posts, many=True, context={'request': request}).data)


# ══ STORIES ═══════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stories_feed(request):
    """Get story bundles for the story rail."""
    following_ids = list(Follow.objects.filter(
        follower=request.user).values_list('following_id', flat=True))
    all_ids = following_ids + [request.user.id]

    now = timezone.now()
    stories = Story.objects.filter(
        author_id__in=all_ids, expires_at__gt=now
    ).select_related('author', 'author__profile').order_by('author_id', '-created_at')

    seen_ids = set(StoryView.objects.filter(
        viewer=request.user).values_list('story_id', flat=True))

    bundles = {}
    for story in stories:
        uid = story.author_id
        if uid not in bundles:
            bundles[uid] = {
                'user': UserMiniSerializer(story.author, context={'request': request}).data,
                'first_story_id': story.pk,
                'all_seen': True,
            }
        if story.pk not in seen_ids:
            bundles[uid]['all_seen'] = False

    result = []
    if request.user.id in bundles:
        result.append(bundles.pop(request.user.id))
    result.extend(sorted(bundles.values(), key=lambda b: b['all_seen']))

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_create_story(request):
    data = request.data
    story = Story.objects.create(
        author       = request.user,
        image        = request.FILES.get('image'),
        caption      = data.get('caption', ''),
        text_color   = data.get('text_color', '#FFFFFF'),
        text_size    = int(data.get('text_size', 24)),
        text_align   = data.get('text_align', 'center'),
        text_style   = data.get('text_style', 'normal'),
        bg_color     = data.get('bg_color', '#000000'),
        bg_gradient  = data.get('bg_gradient', ''),
        filter_name  = data.get('filter_name', 'none'),
        stickers_json= data.get('stickers_json', '[]'),
        poll_question= data.get('poll_question', ''),
        poll_option_a= data.get('poll_option_a', ''),
        poll_option_b= data.get('poll_option_b', ''),
    )
    return Response(StorySerializer(story, context={'request': request}).data, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_story_detail(request, pk):
    try:
        story = Story.objects.get(pk=pk)
    except Story.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    if not story.is_active:
        return Response({'error': 'Story expired.'}, status=410)

    if request.user != story.author:
        StoryView.objects.get_or_create(story=story, viewer=request.user)

    return Response(StorySerializer(story, context={'request': request}).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_story(request, pk):
    try:
        story = Story.objects.get(pk=pk, author=request.user)
    except Story.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    story.delete()
    return Response({'message': 'Story deleted.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_story_like(request, pk):
    try:
        story = Story.objects.get(pk=pk)
    except Story.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    like = StoryLike.objects.filter(user=request.user, story=story)
    if like.exists():
        like.delete(); is_liked = False
    else:
        StoryLike.objects.create(user=request.user, story=story)
        is_liked = True
        if story.author != request.user:
            Notification.objects.create(
                recipient=story.author, actor=request.user, notif_type='story_like',
                message=f'{request.user.username} liked your story.',
                url=f'/stories/{story.pk}/',
            )
    return Response({'is_liked': is_liked, 'likes_count': story.story_likes.count()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_vote_poll(request, pk):
    try:
        story = Story.objects.get(pk=pk)
    except Story.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    choice = request.data.get('choice')
    if choice not in ('a', 'b'):
        return Response({'error': 'Choice must be a or b.'}, status=400)

    StoryPollVote.objects.update_or_create(
        story=story, user=request.user, defaults={'choice': choice})

    return Response({
        'a': story.poll_votes.filter(choice='a').count(),
        'b': story.poll_votes.filter(choice='b').count(),
        'voted': choice,
    })


# ══ CHAT ══════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_chat_inbox(request):
    rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).order_by('-created_at')

    pending = ChatRequest.objects.filter(receiver=request.user, status='pending')\
                .select_related('sender', 'sender__profile')

    return Response({
        'rooms':           ChatRoomSerializer(rooms, many=True, context={'request': request}).data,
        'pending_requests': ChatRequestSerializer(pending, many=True, context={'request': request}).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_send_chat_request(request, username):
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    if target == request.user:
        return Response({'error': 'Cannot chat with yourself.'}, status=400)

    existing_room = ChatRoom.objects.filter(
        Q(user1=request.user, user2=target) | Q(user1=target, user2=request.user)
    ).first()
    if existing_room:
        return Response({'room_id': existing_room.pk, 'already_exists': True})

    req, created = ChatRequest.objects.get_or_create(
        sender=request.user, receiver=target, defaults={'status': 'pending'})
    if created:
        Notification.objects.create(
            recipient=target, actor=request.user, notif_type='chat_request',
            message=f'{request.user.username} wants to chat with you.',
            url='/chat/',
        )
    return Response(ChatRequestSerializer(req, context={'request': request}).data, status=201 if created else 200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_handle_chat_request(request, request_id, action):
    try:
        creq = ChatRequest.objects.get(pk=request_id, receiver=request.user, status='pending')
    except ChatRequest.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    if action == 'accept':
        creq.status = 'accepted'; creq.save()
        room = ChatRoom.get_or_create_for(creq.sender, creq.receiver)
        Notification.objects.create(
            recipient=creq.sender, actor=request.user, notif_type='chat_accepted',
            message=f'{request.user.username} accepted your chat request.',
            url=f'/chat/{room.pk}/',
        )
        return Response({'room_id': room.pk, 'status': 'accepted'})
    else:
        creq.status = 'rejected'; creq.save()
        return Response({'status': 'rejected'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_chat_room(request, room_id):
    try:
        room = ChatRoom.objects.get(pk=room_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)

    if request.user not in (room.user1, room.user2):
        return Response({'error': 'Not allowed.'}, status=403)

    if request.method == 'POST':
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'Message cannot be empty.'}, status=400)
        msg = Message.objects.create(room=room, sender=request.user, text=text)
        return Response(MessageSerializer(msg, context={'request': request}).data, status=201)

    # GET — return messages + mark as read
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    after = request.GET.get('after')
    msgs  = room.messages.all()
    if after:
        msgs = msgs.filter(pk__gt=after)

    return Response(MessageSerializer(msgs, many=True, context={'request': request}).data)


# ══ NOTIFICATIONS ══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response(NotificationSerializer(notifs, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'count': count})
