from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('stories/create/',          views.create_story_view,      name='create'),
    path('stories/<int:pk>/',        views.view_story_view,        name='view'),
    path('stories/<int:pk>/delete/', views.delete_story_view,      name='delete'),
    path('stories/<int:pk>/like/',   views.toggle_story_like_view, name='like'),
    path('stories/<int:pk>/vote/',   views.vote_poll_view,         name='vote_poll'),
]
