from django.contrib import admin

from .models import AuditLog, CoursePayment, Enrollment, EnrollmentCode, InstructorWallet, RevenueShare, WalletTransaction


@admin.register(EnrollmentCode)
class EnrollmentCodeAdmin(admin.ModelAdmin):
    list_display = ("course", "created_by", "max_uses", "used_count", "expires_at", "is_active")

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(Enrollment)
admin.site.register(CoursePayment)
admin.site.register(InstructorWallet)
admin.site.register(WalletTransaction)
admin.site.register(RevenueShare)
admin.site.register(AuditLog)