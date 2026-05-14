from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from courses.models import Course
from .models import CoursePurchase, Enrollment, EnrollmentCode, RevenueShare, InstructorWallet, WalletTransaction, AuditLog


class MarketplaceService:
    @staticmethod
    @transaction.atomic
    def apply_enrollment_code(*, student, course_id, code_value):
        code = EnrollmentCode.objects.select_for_update().select_related('course').filter(code=code_value, course_id=course_id).first()
        if not code or not code.is_active:
            raise ValidationError('Invalid enrollment code.')
        if code.expires_at <= timezone.now() or code.used_count >= code.max_usage:
            raise ValidationError('Enrollment code expired or exhausted.')

        enrollment, created = Enrollment.objects.get_or_create(student=student, course=code.course, defaults={'source': Enrollment.Source.CODE})
        if created:
            code.used_count += 1
            code.save(update_fields=['used_count', 'updated_at'])
            AuditLog.objects.create(actor=student, action='enrollment_code_redeemed', entity_type='EnrollmentCode', entity_id=str(code.id))
        return enrollment

    @staticmethod
    @transaction.atomic
    def settle_purchase(*, purchase: CoursePurchase):
        if purchase.status == CoursePurchase.Status.COMPLETED:
            return purchase
        purchase.status = CoursePurchase.Status.COMPLETED
        purchase.save(update_fields=['status', 'updated_at'])
        Enrollment.objects.get_or_create(student=purchase.student, course=purchase.course, defaults={'purchase': purchase, 'source': Enrollment.Source.PAYMENT})

        gross = purchase.amount
        platform_fee = (gross * Decimal('0.30')).quantize(Decimal('0.01'))
        instructor_earnings = gross - platform_fee
        RevenueShare.objects.update_or_create(
            purchase=purchase,
            defaults={'gross_revenue': gross, 'platform_fee': platform_fee, 'instructor_earnings': instructor_earnings},
        )
        instructor = purchase.course.instructor_user
        wallet, _ = InstructorWallet.objects.get_or_create(instructor=instructor)
        wallet.pending_balance += instructor_earnings
        wallet.save(update_fields=['pending_balance', 'updated_at'])
        WalletTransaction.objects.create(wallet=wallet, amount=instructor_earnings, tx_type=WalletTransaction.Type.REVENUE, reference=str(purchase.id))
        return purchase