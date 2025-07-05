from django.contrib import admin
from django.utils import timezone
from .models import LiveSession, LiveRecording
from courses.admin import BaseModelAdmin  # استيراد BaseModelAdmin من courses
from courses.models import UserProfile
from django.core.exceptions import PermissionDenied
import logging

# إعداد تسجيل الأخطاء
logger = logging.getLogger(__name__)

# إجراء جماعي لتفعيل/تعطيل الجلسات الحية
def toggle_session_active(modeladmin, request, queryset):
    for session in queryset:
        session.is_active = not session.is_active
        session.save()
        status = "active" if session.is_active else "inactive"
        logger.info(f"Live session {session.title} set to {status} by {request.user.username}")
    modeladmin.message_user(request, "تم تغيير حالة الجلسات المحددة بنجاح.")
toggle_session_active.short_description = "تفعيل/تعطيل الجلسات المحددة"

@admin.register(LiveSession)
class LiveSessionAdmin(BaseModelAdmin):
    list_display = ('title', 'instructor', 'start_time', 'end_time', 'is_active', 'has_recording')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('title', 'instructor__username')
    actions = [toggle_session_active]
    raw_id_fields = ('instructor', 'participants')
    list_per_page = 25

    def has_recording(self, obj):
        return obj.recordings.exists()
    has_recording.boolean = True
    has_recording.short_description = "التسجيل متاح"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all live sessions")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering live sessions for instructor {request.user.username}")
                return qs.filter(instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(LiveRecording)
class LiveRecordingAdmin(BaseModelAdmin):
    list_display = ('live_session', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('live_session__title',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all live recordings")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering live recordings for instructor {request.user.username}")
                return qs.filter(live_session__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()