from django.contrib import admin
from .models import Story, StoryView, StoryLike, StoryPollVote

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['author','caption','filter_name','created_at','expires_at','is_active']
    def is_active(self, obj): return obj.is_active
    is_active.boolean = True

admin.site.register(StoryView)
admin.site.register(StoryLike)
admin.site.register(StoryPollVote)
