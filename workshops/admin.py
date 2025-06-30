from django.contrib import admin
from .models import LiveSession, LiveRecording

@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'start_time', 'end_time', 'is_active', 'has_recording']
    list_filter = ['instructor', 'start_time', 'is_active']
    search_fields = ['title', 'instructor__username']

    def has_recording(self, obj):
        return obj.recordings.exists()
    has_recording.boolean = True
    has_recording.short_description = "Recording Available"

@admin.register(LiveRecording)
class LiveRecordingAdmin(admin.ModelAdmin):
    list_display = ['live_session', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['live_session__title']