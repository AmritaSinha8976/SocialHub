from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # OTP Registration (3 steps)
    path('register/',           views.register_step1_view,  name='register'),
    path('register/verify/',    views.register_step2_view,  name='register_verify'),
    path('register/password/',  views.register_step3_view,  name='register_password'),

    # Auth
    path('login/',   views.login_view,  name='login'),
    path('logout/',  views.logout_view, name='logout'),

    # Profile
    path('profile/<str:username>/',             views.profile_view,              name='profile'),
    path('profile/edit/me/',                    views.edit_profile_view,         name='edit_profile'),

    # Follow
    path('follow/<str:username>/',              views.toggle_follow_view,        name='toggle_follow'),
    path('follow-request/<int:request_id>/<str:action>/', views.handle_follow_request_view, name='handle_follow_request'),
    path('follow-requests/',                    views.follow_requests_view,      name='follow_requests'),

    # Block
    path('block/<str:username>/',               views.toggle_block_view,         name='toggle_block'),
    path('blocked/',                            views.blocked_users_view,        name='blocked_list'),

    # Theme
    path('theme/toggle/',                       views.toggle_theme_view,         name='toggle_theme'),

    # Search
    path('search/',                             views.search_users_view,         name='search'),
]
