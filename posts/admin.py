from django.contrib import admin
from .models import Post, Like, Comment, SavedPost

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id','author','caption_preview','likes_count','comments_count','created_at']
    def caption_preview(self, obj): return obj.caption[:60]
    def likes_count(self, obj): return obj.likes_count
    def comments_count(self, obj): return obj.comments_count

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user','post','created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author','post','text_preview','created_at']
    def text_preview(self, obj): return obj.text[:60]

@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ['user','post','created_at']
