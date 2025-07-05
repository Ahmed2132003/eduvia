from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import UserPerformance, LearningRecommendation, PerformanceReport, UserReport
from accounts.models import User
from courses.models import UserProfile
import logging

# إعداد تسجيل الأخطاء
logger = logging.getLogger(__name__)

class BaseModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all data for {self.model.__name__}")
            return qs.select_related('user')
        try:
            profile = UserProfile.objects.get(user=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access to {self.model.__name__}")
            raise PermissionDenied("Only superusers can access this model.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()
        return qs.none()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        logger.warning(f"User {request.user.username} denied view permission for {self.model.__name__}")
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        logger.warning(f"User {request.user.username} denied add permission for {self.model.__name__}")
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        logger.warning(f"User {request.user.username} denied change permission for {self.model.__name__}")
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        logger.warning(f"User {request.user.username} denied delete permission for {self.model.__name__}")
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

@admin.register(UserPerformance)
class UserPerformanceAdmin(BaseModelAdmin):
    list_display = ('user', 'total_courses', 'completed_videos', 'total_coins', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'strength_areas', 'weakness_areas')
    readonly_fields = ('last_updated',)
    fieldsets = (
        (None, {
            'fields': ('user', 'total_courses', 'completed_videos', 'total_coins')
        }),
        ('Performance Analysis', {
            'fields': ('strength_areas', 'weakness_areas')
        }),
        ('Metadata', {
            'fields': ('last_updated',)
        }),
    )

@admin.register(LearningRecommendation)
class LearningRecommendationAdmin(BaseModelAdmin):
    list_display = ('user', 'course', 'priority', 'recommended_at')
    list_filter = ('priority', 'recommended_at', 'course__category')
    search_fields = ('user__username', 'course__title', 'reason')
    readonly_fields = ('recommended_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'course', 'reason', 'priority')
        }),
        ('Metadata', {
            'fields': ('recommended_at',)
        }),
    )

@admin.register(PerformanceReport)
class PerformanceReportAdmin(BaseModelAdmin):
    list_display = ('report_id', 'user', 'generated_at', 'emailed')
    list_filter = ('generated_at', 'emailed')
    search_fields = ('report_id', 'user__username', 'performance_summary')
    readonly_fields = ('report_id', 'generated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'report_id', 'performance_summary', 'recommendations', 'emailed')
        }),
        ('Metadata', {
            'fields': ('generated_at',)
        }),
    )

@admin.register(UserReport)
class UserReportAdmin(BaseModelAdmin):
    list_display = ('report_id', 'user', 'generated_at')
    list_filter = ('generated_at',)
    search_fields = ('report_id', 'user__username')
    readonly_fields = ('report_id', 'generated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'report_id', 'report_file')
        }),
        ('Metadata', {
            'fields': ('generated_at',)
        }),
    )