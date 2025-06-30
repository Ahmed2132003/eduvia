from django.contrib import admin
from .models import Mentorship, MentorshipGroup, GroupRequest, GroupChat, GroupMessage, MentorRating

@admin.register(Mentorship)
class MentorshipAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('mentor__username', 'mentee__username')

@admin.register(MentorshipGroup)
class MentorshipGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'admin__username')

@admin.register(GroupRequest)
class GroupRequestAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('group__name', 'user__username')

@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('group', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('group__name',)

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('chat__group__name', 'sender__username', 'content')

@admin.register(MentorRating)
class MentorRatingAdmin(admin.ModelAdmin):
    list_display = ('mentorship', 'mentee', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('mentorship__mentor__username', 'mentee__username')