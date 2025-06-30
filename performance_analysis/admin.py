from django.contrib import admin
from .models import UserPerformance, LearningRecommendation, PerformanceReport

@admin.register(UserPerformance)
class UserPerformanceAdmin(admin.ModelAdmin):
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(LearningRecommendation)
class LearningRecommendationAdmin(admin.ModelAdmin):
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')

@admin.register(PerformanceReport)
class PerformanceReportAdmin(admin.ModelAdmin):
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')