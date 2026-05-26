from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Enrollment(TimeStampedModel):
    class Source(models.TextChoices):
        ENROLLMENT_CODE = "enrollment_code", "Enrollment Code"
        ADMIN = "admin", "Admin"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="marketplace_enrollments",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="enrollments_v2",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, null=True)
    source = models.CharField(max_length=24, choices=Source.choices)
    payment_reference = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="uq_active_student_course_enrollment",
            )
        ]


class EnrollmentCode(TimeStampedModel):
    code_hash = models.CharField(max_length=64, unique=True)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="enrollment_codes",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_enrollment_codes",
    )
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    @staticmethod
    def hash_code(code: str) -> str:
        normalized = code.strip().lower().encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()


class InstructorWallet(TimeStampedModel):
    instructor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="instructor_wallet",
    )
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )


class WalletTransaction(TimeStampedModel):
    class TxType(models.TextChoices):
        EARNING = "earning", "Earning"
        WITHDRAWAL = "withdrawal", "Withdrawal"

    wallet = models.ForeignKey(
        InstructorWallet, on_delete=models.PROTECT, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=128)
    tx_type = models.CharField(
        max_length=16,
        choices=TxType.choices,
        default=TxType.EARNING,
    )


class WithdrawalRequest(TimeStampedModel):
    """Instructor withdrawal request."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    wallet = models.ForeignKey(
        InstructorWallet,
        on_delete=models.PROTECT,
        related_name="withdrawal_requests",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    withdrawal_code = models.CharField(max_length=128)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Withdrawal #{self.pk} — {self.amount} EGP ({self.status})"


class AuditLog(TimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=80)
    metadata = models.JSONField(default=dict)