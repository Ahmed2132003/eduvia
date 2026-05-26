from django.contrib import admin
from .models import EnrollmentCode, Enrollment, InstructorWallet, WalletTransaction, AuditLog


@admin.register(EnrollmentCode)
class EnrollmentCodeAdmin(admin.ModelAdmin):
    list_display = ['code_hash', 'course', 'created_by', 'max_uses', 'used_count', 'expires_at', 'is_active']
    list_filter = ['is_active', 'course']
    readonly_fields = ['code_hash', 'used_count']

    def save_model(self, request, obj, form, change):
        raw_code = form.data.get('code_hash', '').strip()
        if raw_code and not change:
            obj.code_hash = EnrollmentCode.hash_code(raw_code)
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['code_hash', 'used_count']
        return ['used_count']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'source', 'enrolled_at', 'is_active']
    list_filter = ['source', 'is_active']


@admin.register(InstructorWallet)
class InstructorWalletAdmin(admin.ModelAdmin):
    list_display = ['instructor', 'balance']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'tx_type', 'reference', 'created_at']
    list_filter = ['tx_type']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'entity_type', 'entity_id', 'created_at']
    list_filter = ['action', 'entity_type']