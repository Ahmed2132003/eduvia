from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import AuditLog, Enrollment, EnrollmentCode


class MarketplaceService:

    @staticmethod
    def ensure_superuser_for_code_creation(user):
        if not user.is_superuser:
            raise PermissionDenied("Only superuser can create enrollment codes.")

    @staticmethod
    @transaction.atomic
    def activate_enrollment_code(*, user, course, code):
        code_hash = EnrollmentCode.hash_code(code)
        code_obj = (
            EnrollmentCode.objects
            .select_for_update()
            .filter(code_hash=code_hash, course=course)
            .first()
        )
        if not code_obj or not code_obj.is_active:
            raise ValidationError("Invalid code")
        if code_obj.expires_at <= timezone.now() or code_obj.used_count >= code_obj.max_uses:
            raise ValidationError("Code expired or usage exceeded")

        enrollment, created = Enrollment.objects.get_or_create(
            student=user,
            course=course,
            defaults={
                "source": Enrollment.Source.ENROLLMENT_CODE,
                "payment_reference": f"code:{code_obj.id}",
            },
        )
        if not created:
            return enrollment

        code_obj.used_count += 1
        code_obj.save(update_fields=["used_count", "updated_at"])
        AuditLog.objects.create(
            actor=user,
            action="code_activated",
            entity_type="EnrollmentCode",
            entity_id=str(code_obj.id),
        )
        return enrollment