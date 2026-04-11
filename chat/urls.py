from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/',                                       views.inbox_view,              name='inbox'),
    path('chat/request/<str:username>/',                views.send_chat_request_view,  name='send_request'),
    path('chat/request/<int:request_id>/<str:action>/', views.handle_chat_request_view,name='handle_request'),
    path('chat/<int:room_id>/',                         views.chat_room_view,          name='room'),
]
