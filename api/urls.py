"""
API URL patterns — all prefixed with /api/v1/
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path('auth/otp/request/',       views.api_otp_request,   name='api_otp_request'),
    path('auth/otp/verify/',        views.api_otp_verify,    name='api_otp_verify'),
    path('auth/set-password/',      views.api_set_password,  name='api_set_password'),
    path('auth/login/',             views.api_login,         name='api_login'),
    path('auth/logout/',            views.api_logout,        name='api_logout'),
    path('auth/me/',                views.api_me,            name='api_me'),

    # ── Users ──────────────────────────────────────────────────
    path('users/search/',                               views.api_search_users,   name='api_search'),
    path('users/<str:username>/',                       views.api_user_profile,   name='api_user_profile'),
    path('users/<str:username>/posts/',                 views.api_user_posts,     name='api_user_posts'),
    path('users/<str:username>/follow/',                views.api_toggle_follow,  name='api_toggle_follow'),
    path('users/<str:username>/block/',                 views.api_toggle_block,   name='api_toggle_block'),
    path('users/<str:username>/chat-request/',          views.api_send_chat_request, name='api_send_chat_request'),
    path('profile/edit/',                               views.api_edit_profile,   name='api_edit_profile'),
    path('profile/theme/',                              views.api_toggle_theme,   name='api_toggle_theme'),

    # ── Follow Requests ────────────────────────────────────────
    path('follow-requests/',                            views.api_follow_requests,        name='api_follow_requests'),
    path('follow-requests/<int:request_id>/<str:action>/', views.api_handle_follow_request, name='api_handle_follow_request'),

    # ── Posts ──────────────────────────────────────────────────
    path('posts/feed/',                 views.api_feed,          name='api_feed'),
    path('posts/explore/',              views.api_explore,       name='api_explore'),
    path('posts/create/',               views.api_create_post,   name='api_create_post'),
    path('posts/saved/',                views.api_saved_posts,   name='api_saved_posts'),
    path('posts/<int:pk>/',             views.api_post_detail,   name='api_post_detail'),
    path('posts/<int:pk>/delete/',      views.api_delete_post,   name='api_delete_post'),
    path('posts/<int:pk>/like/',        views.api_toggle_like,   name='api_toggle_like'),
    path('posts/<int:pk>/save/',        views.api_toggle_save,   name='api_toggle_save'),
    path('posts/<int:pk>/comment/',     views.api_add_comment,   name='api_add_comment'),
    path('comments/<int:pk>/delete/',   views.api_delete_comment,name='api_delete_comment'),

    # ── Stories ────────────────────────────────────────────────
    path('stories/',                    views.api_stories_feed,        name='api_stories_feed'),
    path('stories/create/',             views.api_create_story,        name='api_create_story'),
    path('stories/<int:pk>/',           views.api_story_detail,        name='api_story_detail'),
    path('stories/<int:pk>/delete/',    views.api_delete_story,        name='api_delete_story'),
    path('stories/<int:pk>/like/',      views.api_toggle_story_like,   name='api_toggle_story_like'),
    path('stories/<int:pk>/vote/',      views.api_vote_poll,           name='api_vote_poll'),

    # ── Chat ───────────────────────────────────────────────────
    path('chat/',                                           views.api_chat_inbox,        name='api_chat_inbox'),
    path('chat/<int:room_id>/',                             views.api_chat_room,         name='api_chat_room'),
    path('chat/requests/<int:request_id>/<str:action>/',   views.api_handle_chat_request, name='api_handle_chat_request'),

    # ── Notifications ──────────────────────────────────────────
    path('notifications/',              views.api_notifications, name='api_notifications'),
    path('notifications/unread-count/', views.api_unread_count,  name='api_unread_count'),
]
