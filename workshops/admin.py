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

# Part 18: إجراء جماعي لتعليم/إلغاء تعليم تسجيلات كـ "معاينة مجانية"
def toggle_free_preview(modeladmin, request, queryset):
    for recording in queryset:
        recording.is_free_preview = not recording.is_free_preview
        recording.save()
        status = "معاينة مجانية" if recording.is_free_preview else "خاص"
        logger.info(f"Live recording {recording.id} set to {status} by {request.user.username}")
    modeladmin.message_user(request, "تم تغيير حالة المعاينة المجانية للتسجيلات المحددة بنجاح.")
toggle_free_preview.short_description = "تبديل حالة المعاينة المجانية للتسجيلات المحددة"

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
    # Part 18: ضفت is_free_preview في list_display وlist_editable —
    # عشان الأدمن/المدرس (اللي عنده صلاحية وصول للوحة التحكم) يقدر يعلّم
    # أي تسجيل كـ "معاينة مجانية" مباشرة من صفحة القايمة (list view) من
    # غير ما يضطر يفتح كل تسجيل لوحده. list_filter كمان اتضاف عشان
    # يسهّل فلترة التسجيلات المعلّمة بالفعل كمعاينة مجانية.
    # ملحوظة: list_editable محتاج يكون العمود مش أول عمود في list_display
    # (قيد من Django نفسه)، فحطيته في الآخر.
    list_display = ('live_session', 'uploaded_at', 'is_free_preview')
    list_editable = ('is_free_preview',)
    list_filter = ('uploaded_at', 'is_free_preview')
    search_fields = ('live_session__title',)
    actions = [toggle_free_preview]
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