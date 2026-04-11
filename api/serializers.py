"""
API Serializers — convert Django models to/from JSON.
"""

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from users.models import Profile, Follow, FollowRequest, Block
from posts.models import Post, Like, Comment, SavedPost
from stories.models import Story, StoryView, StoryLike
from chat.models import ChatRequest, ChatRoom, Message
from notifications.models import Notification


# ── User & Profile ────────────────────────────────────────────────

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profile
        fields = ['profile_picture', 'bio', 'website', 'location', 'is_private', 'theme']


class UserSerializer(serializers.ModelSerializer):
    profile          = ProfileSerializer(read_only=True)
    followers_count  = serializers.SerializerMethodField()
    following_count  = serializers.SerializerMethodField()
    posts_count      = serializers.SerializerMethodField()
    is_following     = serializers.SerializerMethodField()
    follow_request_status = serializers.SerializerMethodField()
    is_blocked       = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'profile', 'followers_count', 'following_count', 'posts_count',
                  'is_following', 'follow_request_status', 'is_blocked']

    def _req_user(self):
        return self.context.get('request').user

    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj).count()

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_is_following(self, obj):
        u = self._req_user()
        if not u or not u.is_authenticated or u == obj:
            return False
        return Follow.objects.filter(follower=u, following=obj).exists()

    def get_follow_request_status(self, obj):
        u = self._req_user()
        if not u or not u.is_authenticated or u == obj:
            return None
        req = FollowRequest.objects.filter(sender=u, receiver=obj).first()
        return req.status if req else None

    def get_is_blocked(self, obj):
        u = self._req_user()
        if not u or not u.is_authenticated:
            return False
        return Block.objects.filter(blocker=u, blocked=obj).exists()


class UserMiniSerializer(serializers.ModelSerializer):
    """Lightweight user info — used inside other serializers."""
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        try:
            url = obj.profile.profile_picture.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None


# ── Auth ─────────────────────────────────────────────────────────

class OTPRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name  = serializers.CharField(max_length=30, required=False, allow_blank=True)
    username   = serializers.CharField(max_length=150)
    email      = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp   = serializers.CharField(min_length=6, max_length=6)


class SetPasswordSerializer(serializers.Serializer):
    email     = serializers.EmailField()
    password  = serializers.CharField(min_length=8)
    password2 = serializers.CharField(min_length=8)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match.')
        return data


# ── Posts ─────────────────────────────────────────────────────────

class CommentSerializer(serializers.ModelSerializer):
    author   = UserMiniSerializer(read_only=True)
    replies  = serializers.SerializerMethodField()

    class Meta:
        model  = Comment
        fields = ['id', 'author', 'text', 'parent', 'replies', 'created_at']

    def get_replies(self, obj):
        if obj.parent is not None:
            return []
        return CommentSerializer(
            obj.replies.all(), many=True, context=self.context
        ).data


class PostSerializer(serializers.ModelSerializer):
    author         = UserMiniSerializer(read_only=True)
    likes_count    = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked       = serializers.SerializerMethodField()
    is_saved       = serializers.SerializerMethodField()
    image          = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = ['id', 'author', 'image', 'caption', 'likes_count',
                  'comments_count', 'is_liked', 'is_saved', 'created_at']

    def get_is_liked(self, obj):
        u = self.context.get('request').user
        if not u or not u.is_authenticated:
            return False
        return Like.objects.filter(user=u, post=obj).exists()

    def get_is_saved(self, obj):
        u = self.context.get('request').user
        if not u or not u.is_authenticated:
            return False
        return SavedPost.objects.filter(user=u, post=obj).exists()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


# ── Stories ───────────────────────────────────────────────────────

class StorySerializer(serializers.ModelSerializer):
    author     = UserMiniSerializer(read_only=True)
    is_liked   = serializers.SerializerMethodField()
    is_viewed  = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='story_likes.count', read_only=True)
    views_count = serializers.IntegerField(source='views.count', read_only=True)
    image      = serializers.SerializerMethodField()
    is_active  = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Story
        fields = ['id', 'author', 'image', 'caption', 'text_color', 'text_size',
                  'text_align', 'text_style', 'bg_color', 'bg_gradient',
                  'filter_name', 'stickers_json', 'poll_question',
                  'poll_option_a', 'poll_option_b', 'is_liked', 'is_viewed',
                  'likes_count', 'views_count', 'is_active', 'created_at', 'expires_at']

    def get_is_liked(self, obj):
        u = self.context.get('request').user
        return StoryLike.objects.filter(user=u, story=obj).exists() if u.is_authenticated else False

    def get_is_viewed(self, obj):
        u = self.context.get('request').user
        return StoryView.objects.filter(viewer=u, story=obj).exists() if u.is_authenticated else False

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


# ── Chat ──────────────────────────────────────────────────────────

class MessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['id', 'sender', 'text', 'is_read', 'is_mine', 'created_at']

    def get_is_mine(self, obj):
        u = self.context.get('request').user
        return obj.sender == u


class ChatRoomSerializer(serializers.ModelSerializer):
    other_user   = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model  = ChatRoom
        fields = ['id', 'other_user', 'last_message', 'unread_count', 'created_at']

    def get_other_user(self, obj):
        u = self.context.get('request').user
        other = obj.get_other_user(u)
        return UserMiniSerializer(other, context=self.context).data

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return MessageSerializer(msg, context=self.context).data if msg else None

    def get_unread_count(self, obj):
        u = self.context.get('request').user
        return obj.messages.filter(is_read=False).exclude(sender=u).count()


class ChatRequestSerializer(serializers.ModelSerializer):
    sender   = UserMiniSerializer(read_only=True)
    receiver = UserMiniSerializer(read_only=True)

    class Meta:
        model  = ChatRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']


# ── Notifications ─────────────────────────────────────────────────

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserMiniSerializer(read_only=True)

    class Meta:
        model  = Notification
        fields = ['id', 'actor', 'notif_type', 'message', 'url', 'is_read', 'created_at']


# ── Follow Request ────────────────────────────────────────────────

class FollowRequestSerializer(serializers.ModelSerializer):
    sender   = UserMiniSerializer(read_only=True)
    receiver = UserMiniSerializer(read_only=True)

    class Meta:
        model  = FollowRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']
