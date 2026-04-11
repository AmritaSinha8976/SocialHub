"""
Users app views — OTP registration, auth, profiles, follow, block, theme.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .forms import (EmailOTPRequestForm, OTPVerifyForm, SetPasswordForm,
                    LoginForm, ProfileUpdateForm, UserUpdateForm)
from .models import Follow, Profile, FollowRequest, Block, OTPVerification
from notifications.models import Notification


# ─── OTP Registration (3-step) ───────────────────────────────────────────────

def register_step1_view(request):
    """Step 1: Collect name, username, email → send OTP."""
    if request.user.is_authenticated:
        return redirect('posts:feed')

    if request.method == 'POST':
        form = EmailOTPRequestForm(request.POST)
        if form.is_valid():
            email      = form.cleaned_data['email']
            username   = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name  = form.cleaned_data.get('last_name','')

            # Generate + store OTP (overwrite if already exists for this email)
            otp_code = OTPVerification.generate_otp()
            OTPVerification.objects.filter(email=email).delete()
            OTPVerification.objects.create(
                email=email,
                otp=otp_code,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_verified=False,
                expires_at=timezone.now() + timedelta(minutes=10),
            )

            # Send OTP email
            try:
                send_mail(
                    subject='Your SocialHub OTP Code',
                    message=(
                        f'Hi {first_name},\n\n'
                        f'Your OTP code is: {otp_code}\n\n'
                        f'This code expires in 10 minutes.\n\n'
                        f'— SocialHub Team'
                    ),
                    from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'noreply@socialhub.com'),
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception:
                # In dev, EMAIL_BACKEND = console — print to terminal; don't block signup
                pass

            request.session['otp_email'] = email
            messages.success(request, f'OTP sent to {email}. Check your inbox (or console in dev).')
            return redirect('users:register_verify')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = EmailOTPRequestForm()

    return render(request, 'users/register_step1.html', {'form': form})


def register_step2_view(request):
    """Step 2: Enter OTP code."""
    email = request.session.get('otp_email')
    if not email:
        return redirect('users:register')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data['otp'].strip()
            try:
                record = OTPVerification.objects.get(email=email, is_verified=False)
            except OTPVerification.DoesNotExist:
                messages.error(request, 'OTP not found. Please restart registration.')
                return redirect('users:register')

            if record.is_expired():
                messages.error(request, 'OTP expired. Please request a new one.')
                return redirect('users:register')

            if record.otp != entered:
                messages.error(request, 'Incorrect OTP. Please try again.')
            else:
                record.is_verified = True
                record.save()
                request.session['otp_verified_email'] = email
                return redirect('users:register_password')
    else:
        form = OTPVerifyForm()

    return render(request, 'users/register_step2.html', {'form': form, 'email': email})


def register_step3_view(request):
    """Step 3: Set password, create account."""
    email = request.session.get('otp_verified_email')
    if not email:
        return redirect('users:register')

    try:
        record = OTPVerification.objects.get(email=email, is_verified=True)
    except OTPVerification.DoesNotExist:
        return redirect('users:register')

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username   = record.username,
                email      = record.email,
                password   = form.cleaned_data['password1'],
                first_name = record.first_name,
                last_name  = record.last_name,
            )
            record.delete()
            request.session.pop('otp_email', None)
            request.session.pop('otp_verified_email', None)
            login(request, user)
            messages.success(request, f'Welcome to SocialHub, {user.username}! 🎉')
            return redirect('posts:feed')
    else:
        form = SetPasswordForm()

    return render(request, 'users/register_step3.html', {'form': form, 'username': record.username})


# ─── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next','posts:feed'))
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm(request)
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')


# ─── Profile ──────────────────────────────────────────────────────────────────

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _   = Profile.objects.get_or_create(user=profile_user)

    # Block check
    if request.user.is_authenticated and request.user != profile_user:
        if Block.is_blocked(request.user, profile_user):
            return render(request, 'users/blocked.html', {'profile_user': profile_user})

    posts = profile_user.posts.all().order_by('-created_at')
    is_following = follow_request_status = None
    can_view = profile.can_view_posts(request.user)

    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
        req = FollowRequest.objects.filter(sender=request.user, receiver=profile_user).first()
        if req:
            follow_request_status = req.status

    if not can_view:
        posts = []

    is_blocked_by_me = False
    if request.user.is_authenticated:
        is_blocked_by_me = Block.objects.filter(blocker=request.user, blocked=profile_user).exists()

    return render(request, 'users/profile.html', {
        'profile_user': profile_user, 'profile': profile, 'posts': posts,
        'is_following': is_following, 'is_own_profile': request.user == profile_user,
        'follow_request_status': follow_request_status, 'can_view': can_view,
        'followers':  Follow.objects.filter(following=profile_user).select_related('follower'),
        'following':  Follow.objects.filter(follower=profile_user).select_related('following'),
        'is_blocked_by_me': is_blocked_by_me,
    })


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form    = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save(); profile_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('users:profile', username=request.user.username)
    else:
        user_form    = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'users/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


# ─── Block ────────────────────────────────────────────────────────────────────

@login_required
def toggle_block_view(request, username):
    if request.method != 'POST':
        return redirect('users:profile', username=username)
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('users:profile', username=username)

    block = Block.objects.filter(blocker=request.user, blocked=target)
    if block.exists():
        block.delete()
        messages.success(request, f'You unblocked {target.username}.')
    else:
        Block.objects.create(blocker=request.user, blocked=target)
        # Also remove follow relationship in both directions
        Follow.objects.filter(
            Q(follower=request.user, following=target) |
            Q(follower=target, following=request.user)
        ).delete()
        FollowRequest.objects.filter(
            Q(sender=request.user, receiver=target) |
            Q(sender=target, receiver=request.user)
        ).delete()
        messages.success(request, f'You blocked {target.username}.')
    return redirect('users:profile', username=username)


@login_required
def blocked_users_view(request):
    blocked = Block.objects.filter(blocker=request.user).select_related('blocked','blocked__profile')
    return render(request, 'users/blocked_list.html', {'blocked_list': blocked})


# ─── Follow ───────────────────────────────────────────────────────────────────

@login_required
def toggle_follow_view(request, username):
    if request.method != 'POST':
        return redirect('users:profile', username=username)
    target = get_object_or_404(User, username=username)
    if request.user == target:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    if Block.is_blocked(request.user, target):
        return JsonResponse({'error': 'Blocked'}, status=403)

    target_profile, _ = Profile.objects.get_or_create(user=target)
    existing = Follow.objects.filter(follower=request.user, following=target)

    if existing.exists():
        existing.delete()
        FollowRequest.objects.filter(sender=request.user, receiver=target).delete()
        return _ajax_or_redirect(request, username, {
            'is_following': False, 'follow_request_status': None,
            'followers_count': Follow.objects.filter(following=target).count(),
        })

    if target_profile.is_private:
        freq, created = FollowRequest.objects.get_or_create(
            sender=request.user, receiver=target, defaults={'status':'pending'})
        if created:
            Notification.objects.create(
                recipient=target, actor=request.user, notif_type='follow_request',
                message=f'{request.user.username} sent you a follow request.',
                url='/follow-requests/',
            )
        return _ajax_or_redirect(request, username, {
            'is_following': False, 'follow_request_status': freq.status,
            'followers_count': Follow.objects.filter(following=target).count(),
        })

    Follow.objects.get_or_create(follower=request.user, following=target)
    Notification.objects.create(
        recipient=target, actor=request.user, notif_type='follow_request',
        message=f'{request.user.username} started following you.',
        url=f'/profile/{request.user.username}/',
    )
    return _ajax_or_redirect(request, username, {
        'is_following': True, 'follow_request_status': 'accepted',
        'followers_count': Follow.objects.filter(following=target).count(),
    })


@login_required
def handle_follow_request_view(request, request_id, action):
    freq = get_object_or_404(FollowRequest, pk=request_id, receiver=request.user, status='pending')
    if action == 'accept':
        freq.status = 'accepted'; freq.save()
        Follow.objects.get_or_create(follower=freq.sender, following=request.user)
        Notification.objects.create(
            recipient=freq.sender, actor=request.user, notif_type='follow_accepted',
            message=f'{request.user.username} accepted your follow request.',
            url=f'/profile/{request.user.username}/',
        )
        messages.success(request, f'Accepted {freq.sender.username}\'s request.')
    else:
        freq.status = 'rejected'; freq.save()
        messages.info(request, f'Rejected {freq.sender.username}\'s request.')
    return redirect(request.META.get('HTTP_REFERER', 'notifications:list'))


@login_required
def follow_requests_view(request):
    pending = FollowRequest.objects.filter(
        receiver=request.user, status='pending'
    ).select_related('sender','sender__profile')
    return render(request, 'users/follow_requests.html', {'pending_requests': pending})


# ─── Theme ────────────────────────────────────────────────────────────────────

@login_required
def toggle_theme_view(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.theme = 'dark' if profile.theme == 'light' else 'light'
        profile.save(update_fields=['theme'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'theme': profile.theme})
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ─── Search ───────────────────────────────────────────────────────────────────

def search_users_view(request):
    query = request.GET.get('q','').strip()
    users = []
    if query:
        blocked_ids = []
        if request.user.is_authenticated:
            blocked_ids = list(Block.objects.filter(
                Q(blocker=request.user) | Q(blocked=request.user)
            ).values_list('blocker_id','blocked_id'))
            blocked_ids = list({uid for pair in blocked_ids for uid in pair})

        users = User.objects.filter(username__icontains=query).exclude(
            id__in=blocked_ids
        ).exclude(
            id=request.user.id if request.user.is_authenticated else 0
        )[:20]
    return render(request, 'users/search.html', {'users': users, 'query': query})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _ajax_or_redirect(request, username, data):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    return redirect('users:profile', username=username)
