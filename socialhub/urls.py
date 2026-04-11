from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web app URLs
    path('', include('users.urls',         namespace='users')),
    path('', include('posts.urls',         namespace='posts')),
    path('', include('stories.urls',       namespace='stories')),
    path('', include('chat.urls',          namespace='chat')),
    path('', include('notifications.urls', namespace='notifications')),

    # REST API for mobile app
    path('api/v1/', include('api.urls')),

    # JWT token refresh (used by React Native axios interceptor)
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
