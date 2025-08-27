# chatbot/admin.py
from django.contrib import admin
from .models import BotChat, BotMessage

class BotMessageInline(admin.TabularInline):
    model = BotMessage
    extra = 0
    fields = ['user_message', 'bot_response', 'sent_at']
    readonly_fields = ['sent_at']
    can_delete = True

@admin.register(BotChat)
class BotChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['user__username', 'title']
    inlines = [BotMessageInline]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'user_message', 'sent_at']
    list_filter = ['chat__user', 'sent_at']
    search_fields = ['user_message', 'bot_response']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'