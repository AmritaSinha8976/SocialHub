from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/',              views.notifications_list_view, name='list'),
    path('notifications/<int:pk>/read/',views.mark_read_view,          name='mark_read'),
    path('notifications/count/',        views.unread_count_view,       name='count'),
]
