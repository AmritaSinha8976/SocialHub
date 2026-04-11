from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Follow, FollowRequest, Block, OTPVerification


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ['bio','profile_picture','website','location','is_private','theme']


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username','email','first_name','is_staff','date_joined']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','is_private','theme','location']
    list_filter  = ['is_private','theme']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower','following','created_at']

@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ['sender','receiver','status','created_at']
    list_filter  = ['status']

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['blocker','blocked','created_at']
    search_fields = ['blocker__username','blocked__username']

@admin.register(OTPVerification)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['email','username','otp','is_verified','expires_at']
    list_filter  = ['is_verified']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
