from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import AuditLog, CoursePayment, Enrollment, EnrollmentCode, InstructorWallet, RevenueShare, WalletTransaction


class MarketplaceService:
    @staticmethod
    def ensure_superuser_for_code_creation(user):
        if not user.is_superuser:
            raise PermissionDenied("Only superuser can create enrollment codes.")

    @staticmethod
    @transaction.atomic
    def activate_enrollment_code(*, user, course, code):
        code_hash = EnrollmentCode.hash_code(code)
        code_obj = EnrollmentCode.objects.select_for_update().filter(code_hash=code_hash, course=course).first()
        if not code_obj or not code_obj.is_active:
            raise ValidationError("Invalid code")
        if code_obj.expires_at <= timezone.now() or code_obj.used_count >= code_obj.max_uses:
            raise ValidationError("Code expired or usage exceeded")

        enrollment, created = Enrollment.objects.get_or_create(
            student=user,
            course=course,
            defaults={"source": Enrollment.Source.ENROLLMENT_CODE, "payment_reference": f"code:{code_obj.id}"},
        )
        if not created:
            return enrollment
        code_obj.used_count += 1
        code_obj.save(update_fields=["used_count", "updated_at"])
        AuditLog.objects.create(actor=user, action="code_activated", entity_type="EnrollmentCode", entity_id=str(code_obj.id))
        return enrollment

    @staticmethod
    def create_paymob_checkout(*, user, course):
        tx_id = f"paymob-{uuid.uuid4()}"
        payment = CoursePayment.objects.create(user=user, course=course, amount=course.price, transaction_id=tx_id)
        return {"transaction_id": payment.transaction_id, "redirect_url": f"/payment/paymob/{payment.transaction_id}/"}

    @staticmethod
    @transaction.atomic
    def finalize_payment(*, payment: CoursePayment, webhook_payload: dict):
        payment = CoursePayment.objects.select_for_update().select_related("course").get(pk=payment.pk)
        if payment.payment_status == CoursePayment.Status.PAID:
            return payment
        payment.payment_status = CoursePayment.Status.PAID
        payment.verified = True
        payment.paid_at = timezone.now()
        payment.save(update_fields=["payment_status", "verified", "paid_at", "updated_at"])

        Enrollment.objects.get_or_create(
            student=payment.user,
            course=payment.course,
            defaults={"source": Enrollment.Source.PAYMOB, "payment_reference": payment.transaction_id},
        )

        instructor_amount = (payment.amount * Decimal("0.70")).quantize(Decimal("0.01"))
        platform_amount = payment.amount - instructor_amount
        wallet, _ = InstructorWallet.objects.select_for_update().get_or_create(instructor=payment.course.instructor_user)
        wallet.balance += instructor_amount
        wallet.save(update_fields=["balance", "updated_at"])
        RevenueShare.objects.update_or_create(payment=payment, defaults={"instructor_amount": instructor_amount, "platform_amount": platform_amount})
        WalletTransaction.objects.create(wallet=wallet, amount=instructor_amount, payment=payment, reference=payment.transaction_id)
        AuditLog.objects.create(actor=payment.user, action="payment_verified", entity_type="CoursePayment", entity_id=str(payment.id), metadata=webhook_payload)
        return payment