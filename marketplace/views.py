"""
marketplace/views.py
====================
Preserves all existing API views exactly.
Adds three new HTML page views:
  - access_info_page        → /api/marketplace/my/access-info/
  - my_courses_page         → /api/marketplace/my/courses/
  - instructor_wallet_page  → /api/marketplace/wallet/
"""

from __future__ import annotations

import hmac
import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, CourseEnrollment
from .models import (
    CoursePayment,
    Enrollment,
    InstructorWallet,
    WalletTransaction,
    WithdrawalRequest,
)
from .serializers import (
    ActivateCodeSerializer,
    EnrollmentSerializer,
    WebhookSerializer,
)
from .services import MarketplaceService


# ══════════════════════════════════════════════════════════════════════════════
# EXISTING API VIEWS — untouched
# ══════════════════════════════════════════════════════════════════════════════

class CheckoutPaymobAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        return Response(
            MarketplaceService.create_paymob_checkout(user=request.user, course=course),
            status=201,
        )


class ActivateCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        serializer = ActivateCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(Course, id=course_id)
        enrollment = MarketplaceService.activate_enrollment_code(
            user=request.user,
            course=course,
            code=serializer.validated_data["code"],
        )
        return Response(EnrollmentSerializer(enrollment).data)


class PaymentWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        secret = getattr(settings, "PAYMOB_HMAC_SECRET", "")
        expected = hmac.new(
            secret.encode(),
            serializer.validated_data["transaction_id"].encode(),
            "sha512",
        ).hexdigest()
        if not hmac.compare_digest(expected, serializer.validated_data["hmac"]):
            return Response({"detail": "invalid signature"}, status=400)
        payment = get_object_or_404(
            CoursePayment,
            transaction_id=serializer.validated_data["transaction_id"],
        )
        MarketplaceService.finalize_payment(
            payment=payment,
            webhook_payload=serializer.validated_data["payload"],
        )
        return Response({"status": "ok"})


class MyEnrollmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = Enrollment.objects.filter(
            student=request.user, is_active=True
        ).select_related("course")
        return Response(EnrollmentSerializer(rows, many=True).data)


class AccessStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "has_access": Enrollment.objects.filter(
                    student=request.user, is_active=True
                ).exists()
            }
        )


@login_required
def access_restricted_page(request):
    return render(request, "marketplace/access_restricted.html")


@login_required
def checkout_page(request):
    course = (
        get_object_or_404(Course, id=request.GET.get("course_id"))
        if request.GET.get("course_id")
        else None
    )
    return render(
        request,
        "marketplace/checkout.html",
        {
            "course": course,
            "courses": Course.objects.all().order_by("-created_at")[:20],
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# NEW VIEW 1 — Access Info Page
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def access_info_page(request):
    """
    Shows the logged-in user's own course access information.
    Students see their enrollments + payment history.
    Instructors also see their own enrollments.
    NEVER exposes other users' data.
    """
    user = request.user

    # Marketplace enrollments (secure: filtered strictly by request.user)
    marketplace_enrollments = (
        Enrollment.objects.filter(student=user)
        .select_related("course")
        .order_by("-enrolled_at")
    )

    # Legacy course enrollments
    legacy_enrollments = (
        CourseEnrollment.objects.filter(user=user)
        .select_related("course")
        .order_by("-enrolled_at")
    )

    # Paid payments only
    payments = (
        CoursePayment.objects.filter(user=user, payment_status=CoursePayment.Status.PAID)
        .select_related("course")
        .order_by("-paid_at")
    )

    # Merge active course IDs to build a unified access list
    active_course_ids = set(
        marketplace_enrollments.filter(is_active=True).values_list("course_id", flat=True)
    )
    legacy_course_ids = set(
        legacy_enrollments.values_list("course_id", flat=True)
    )
    all_active_ids = active_course_ids | legacy_course_ids

    total_active = len(all_active_ids)
    has_any_access = total_active > 0

    context = {
        "marketplace_enrollments": marketplace_enrollments,
        "legacy_enrollments": legacy_enrollments,
        "payments": payments,
        "total_active": total_active,
        "has_any_access": has_any_access,
    }
    return render(request, "marketplace/access_restricted.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# NEW VIEW 2 — Instructor Wallet Page
# ══════════════════════════════════════════════════════════════════════════════

def _is_instructor(user) -> bool:
    """True when the user is an instructor (or superuser)."""
    if user.is_superuser:
        return True
    try:
        return user.courses_profile.role == "instructor"
    except Exception:
        pass
    try:
        return user.role == "instructor"
    except Exception:
        pass
    return False


@login_required
def instructor_wallet_page(request):
    """
    Instructor-only page.
    Shows ONLY the logged-in instructor's wallet data.
    All querysets are filtered strictly by request.user.
    """
    user = request.user

    # ── Backend authorization — not just frontend hiding ──
    if not _is_instructor(user):
        messages.error(request, "Access denied. This page is for instructors only.")
        return redirect("courses:courses")

    # ── Wallet — get or create safely ──
    wallet, _ = InstructorWallet.objects.get_or_create(
        instructor=user,
        defaults={"balance": Decimal("0.00")},
    )

    # ── Transactions (strictly this instructor's wallet) ──
    transactions = (
        WalletTransaction.objects.filter(wallet=wallet)
        .select_related("payment__course")
        .order_by("-created_at")[:50]
    )

    # ── Per-course earnings (strictly this instructor's courses) ──
    instructor_courses = Course.objects.filter(instructor_user=user).prefetch_related(
        "course_payments", "enrollments_v2"
    )

    course_stats = []
    for course in instructor_courses:
        paid_payments = CoursePayment.objects.filter(
            course=course, payment_status=CoursePayment.Status.PAID
        )
        student_count = paid_payments.values("user").distinct().count()
        revenue = paid_payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        instructor_share = (revenue * Decimal("0.70")).quantize(Decimal("0.01"))
        course_stats.append(
            {
                "course": course,
                "student_count": student_count,
                "revenue": revenue,
                "instructor_share": instructor_share,
            }
        )

    # ── Withdrawal requests (strictly this wallet) ──
    withdrawal_requests = WithdrawalRequest.objects.filter(wallet=wallet).order_by(
        "-created_at"
    )[:20]

    # ── Total withdrawn ──
    total_withdrawn = (
        WithdrawalRequest.objects.filter(
            wallet=wallet, status=WithdrawalRequest.Status.APPROVED
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    # ── Handle withdrawal form POST ──
    withdrawal_error = None
    withdrawal_success = None

    if request.method == "POST":
        raw_amount = request.POST.get("amount", "").strip()
        withdrawal_code = request.POST.get("withdrawal_code", "").strip()

        if not withdrawal_code:
            withdrawal_error = "Withdrawal code is required."
        else:
            try:
                amount = Decimal(raw_amount)
                if amount <= 0:
                    withdrawal_error = "Amount must be greater than zero."
                elif amount > wallet.balance:
                    withdrawal_error = (
                        f"Insufficient balance. Available: {wallet.balance} EGP."
                    )
                else:
                    WithdrawalRequest.objects.create(
                        wallet=wallet,
                        amount=amount,
                        withdrawal_code=withdrawal_code,
                        status=WithdrawalRequest.Status.PENDING,
                    )
                    withdrawal_success = (
                        f"Withdrawal request of {amount} EGP submitted successfully."
                    )
            except (InvalidOperation, ValueError):
                withdrawal_error = "Please enter a valid numeric amount."

    context = {
        "wallet": wallet,
        "transactions": transactions,
        "course_stats": course_stats,
        "withdrawal_requests": withdrawal_requests,
        "total_withdrawn": total_withdrawn,
        "withdrawal_error": withdrawal_error,
        "withdrawal_success": withdrawal_success,
    }
    return render(request, "marketplace/instructor_wallet.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# NEW VIEW 3 — My Courses Page (dynamic: student vs instructor)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def my_courses_page(request):
    """
    Dynamic page:
    - Students see their enrolled courses + apply enrollment code.
    - Instructors see the courses they created + quick stats.
    All data strictly filtered by request.user.
    """
    user = request.user
    is_instructor = _is_instructor(user)

    # ── Handle enrollment code POST (students only) ──
    if request.method == "POST" and request.POST.get("action") == "apply_code":
        course_id = request.POST.get("course_id")
        code = request.POST.get("code", "").strip()
        try:
            course = get_object_or_404(Course, id=int(course_id))
            MarketplaceService.activate_enrollment_code(
                user=user, course=course, code=code
            )
            messages.success(request, f"Enrolled in '{course.title}' successfully!")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect(request.path)

    if is_instructor:
        # ── INSTRUCTOR BRANCH ──
        # Courses created by this instructor (strictly filtered)
        instructor_courses = Course.objects.filter(instructor_user=user).order_by(
            "-created_at"
        )

        course_data = []
        for course in instructor_courses:
            # Count distinct students from marketplace enrollments
            mp_students = (
                Enrollment.objects.filter(course=course, is_active=True)
                .values("student")
                .distinct()
                .count()
            )
            legacy_students = (
                CourseEnrollment.objects.filter(course=course)
                .values("user")
                .distinct()
                .count()
            )
            total_students = max(mp_students, legacy_students)

            # Revenue from confirmed payments
            revenue = (
                CoursePayment.objects.filter(
                    course=course, payment_status=CoursePayment.Status.PAID
                ).aggregate(total=Sum("amount"))["total"]
                or Decimal("0.00")
            )

            course_data.append(
                {
                    "course": course,
                    "student_count": total_students,
                    "revenue": revenue,
                }
            )

        context = {
            "is_instructor": True,
            "course_data": course_data,
        }

    else:
        # ── STUDENT BRANCH ──
        # Marketplace enrollments (strictly this student)
        marketplace_enrollments = (
            Enrollment.objects.filter(student=user, is_active=True)
            .select_related("course")
            .order_by("-enrolled_at")
        )

        # Legacy enrollments
        legacy_enrollments = (
            CourseEnrollment.objects.filter(user=user)
            .select_related("course")
            .order_by("-enrolled_at")
        )

        # Deduplicate by course ID — prefer marketplace record
        seen = set()
        combined_enrollments = []
        for e in marketplace_enrollments:
            if e.course_id not in seen:
                seen.add(e.course_id)
                combined_enrollments.append(
                    {
                        "course": e.course,
                        "source": e.get_source_display(),
                        "enrolled_at": e.enrolled_at,
                        "is_marketplace": True,
                    }
                )
        for e in legacy_enrollments:
            if e.course_id not in seen:
                seen.add(e.course_id)
                combined_enrollments.append(
                    {
                        "course": e.course,
                        "source": "Direct",
                        "enrolled_at": e.enrolled_at,
                        "is_marketplace": False,
                    }
                )

        context = {
            "is_instructor": False,
            "enrollments": combined_enrollments,
        }

    return render(request, "marketplace/my_courses.html", context)