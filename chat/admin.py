from django.contrib import admin
from .models import ChatRequest, ChatRoom, Message

@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status', 'created_at']
    list_filter  = ['status']

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'text_preview', 'is_read', 'created_at']
    def text_preview(self, obj): return obj.text[:60]
