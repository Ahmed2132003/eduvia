from django.contrib import admin
from django.utils import timezone
from .models import EnrollmentCode, Enrollment, InstructorWallet, WalletTransaction, RevenueShare, AuditLog, CoursePayment


@admin.register(EnrollmentCode)
class EnrollmentCodeAdmin(admin.ModelAdmin):
    list_display = ['code_hash', 'course', 'created_by', 'max_uses', 'used_count', 'expires_at', 'is_active']
    list_filter = ['is_active', 'course']
    readonly_fields = ['code_hash', 'used_count']

    def save_model(self, request, obj, form, change):
        # لو بيضيف كود جديد، خد الـ raw code من الـ input وحوله لـ hash
        raw_code = form.data.get('code_hash', '').strip()
        if raw_code and not change:
            # كود جديد - حوله لـ hash
            obj.code_hash = EnrollmentCode.hash_code(raw_code)
        elif raw_code and change:
            # تعديل - لو مش بدو يغير الـ hash اتركه
            pass
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # تعديل
            return ['code_hash', 'used_count']
        return ['used_count']  # إضافة جديدة


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'source', 'enrolled_at', 'is_active']
    list_filter = ['source', 'is_active']


@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'payment_status', 'verified', 'paid_at']
    list_filter = ['payment_status', 'verified']


@admin.register(InstructorWallet)
class InstructorWalletAdmin(admin.ModelAdmin):
    list_display = ['instructor', 'balance']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'entity_type', 'entity_id', 'created_at']
    list_filter = ['action', 'entity_type']