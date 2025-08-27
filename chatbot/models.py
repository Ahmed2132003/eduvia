# chatbot/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class BotChat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bot_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, blank=True, default="New Chat")

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Chat {self.id} for {self.user.username} at {self.created_at}"

class BotMessage(models.Model):
    chat = models.ForeignKey(BotChat, on_delete=models.CASCADE, related_name='messages')
    user_message = models.TextField()
    bot_response = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in Chat {self.chat.id} at {self.sent_at}"