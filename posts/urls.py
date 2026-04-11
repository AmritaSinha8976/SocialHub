from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('',                              views.feed_view,          name='feed'),
    path('explore/',                      views.explore_view,       name='explore'),
    path('post/new/',                     views.create_post_view,   name='create_post'),
    path('post/<int:pk>/',                views.post_detail_view,   name='post_detail'),
    path('post/<int:pk>/delete/',         views.delete_post_view,   name='delete_post'),
    path('post/<int:pk>/like/',           views.toggle_like_view,   name='toggle_like'),
    path('post/<int:pk>/save/',           views.toggle_save_view,   name='toggle_save'),
    path('post/<int:pk>/comment/',        views.add_comment_view,   name='add_comment'),
    path('comment/<int:pk>/delete/',      views.delete_comment_view,name='delete_comment'),
    path('saved/',                        views.saved_posts_view,   name='saved_posts'),
]
