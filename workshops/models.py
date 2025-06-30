from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string

class LiveSession(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='live_sessions',
        limit_choices_to={'role': 'instructor'}
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='live_sessions_participated',
        blank=True
    )
    meet_link = models.URLField(max_length=500, blank=True, help_text="Google Meet link for the live session")
    session_image = models.ImageField(upload_to='media/live_session_images/', blank=True, null=True, help_text="Upload an image for the session")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.start_time}"

class LiveRecording(models.Model):
    live_session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='recordings')
    video_file = models.FileField(upload_to='media/live_recordings/', help_text="Upload the recorded video after the live session")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording for {self.live_session.title} - {self.uploaded_at}"