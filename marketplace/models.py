import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CoursePurchase(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='course_purchases')
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT, related_name='purchases')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default='EGP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    idempotency_key = models.CharField(max_length=128, unique=True)


class Enrollment(TimeStampedModel):
    class Source(models.TextChoices):
        PAYMENT = 'payment', 'Payment'
        CODE = 'code', 'Enrollment Code'
        ADMIN = 'admin', 'Admin'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='marketplace_enrollments')
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT, related_name='marketplace_enrollments')
    purchase = models.OneToOneField(CoursePurchase, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollment')
    source = models.CharField(max_length=16, choices=Source.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'course'], name='uq_marketplace_enrollment')]


class Payment(TimeStampedModel):
    class Provider(models.TextChoices):
        PAYMOB = 'paymob', 'Paymob'

    class Status(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        AUTHORIZED = 'authorized', 'Authorized'
        CAPTURED = 'captured', 'Captured'
        FAILED = 'failed', 'Failed'

    purchase = models.OneToOneField(CoursePurchase, on_delete=models.PROTECT, related_name='payment')
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.PAYMOB)
    provider_order_id = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)


class PaymentTransaction(TimeStampedModel):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='transactions')
    provider_txn_id = models.CharField(max_length=128, unique=True)
    raw_payload = models.JSONField(default=dict)
    signature_valid = models.BooleanField(default=False)


class EnrollmentCode(TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT, related_name='enrollment_codes')
    expires_at = models.DateTimeField()
    max_usage = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class InstructorWallet(TimeStampedModel):
    instructor = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='wallet')
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    withdrawn_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


class WalletTransaction(TimeStampedModel):
    class Type(models.TextChoices):
        REVENUE = 'revenue', 'Revenue'
        RELEASE = 'release', 'Release'
        WITHDRAW = 'withdraw', 'Withdraw'

    wallet = models.ForeignKey(InstructorWallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tx_type = models.CharField(max_length=16, choices=Type.choices)
    reference = models.CharField(max_length=128)


class WithdrawalRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed'

    wallet = models.ForeignKey(InstructorWallet, on_delete=models.PROTECT, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    collection_code = models.CharField(max_length=64)


class RevenueShare(TimeStampedModel):
    purchase = models.OneToOneField(CoursePurchase, on_delete=models.PROTECT, related_name='revenue_share')
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2)
    instructor_earnings = models.DecimalField(max_digits=12, decimal_places=2)


class PayoutApproval(TimeStampedModel):
    withdrawal_request = models.OneToOneField(WithdrawalRequest, on_delete=models.PROTECT, related_name='approval')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='approved_payouts')
    notes = models.TextField(blank=True)


class AuditLog(TimeStampedModel):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=128)
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict)