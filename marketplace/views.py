from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, CourseEnrollment
from core.ownership import is_course_owner
from .models import (
    Enrollment,
    InstructorWallet,
    WalletTransaction,
    WithdrawalRequest,
)
from .serializers import (
    ActivateCodeSerializer,
    EnrollmentSerializer,
)
from .services import MarketplaceService


# ══════════════════════════════════════════════════════════════════════════════
# API VIEWS
# ══════════════════════════════════════════════════════════════════════════════

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
        has_access = (
            Course.objects.filter(instructor=request.user.username).exists()
            or Course.objects.filter(instructor_user=request.user).exists()
            or Enrollment.objects.filter(
                student=request.user, is_active=True
            ).exists()
        )
        return Response({"has_access": has_access})


# ══════════════════════════════════════════════════════════════════════════════
# HTML VIEWS
# ══════════════════════════════════════════════════════════════════════════════

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
    if course and request.user.is_authenticated and is_course_owner(request.user, course):
        messages.info(request, "أنت صاحب هذا الكورس، لديك وصول كامل تلقائياً.")
        from django.utils.text import slugify
        from courses.utils import clean_text
        return redirect(
            'courses:course_details',
            course_id=course.id,
            course_slug=slugify(clean_text(course.title), allow_unicode=True) or 'default-title',
        )
    return render(
        request,
        "marketplace/checkout.html",
        {
            "course": course,
            "courses": Course.objects.all().order_by("-created_at")[:20],
        },
    )


@login_required
def access_info_page(request):
    user = request.user

    marketplace_enrollments = (
        Enrollment.objects.filter(student=user)
        .select_related("course")
        .order_by("-enrolled_at")
    )

    legacy_enrollments = (
        CourseEnrollment.objects.filter(user=user)
        .select_related("course")
        .order_by("-enrolled_at")
    )

    active_course_ids = set(
        marketplace_enrollments.filter(is_active=True).values_list("course_id", flat=True)
    )
    legacy_course_ids = set(
        legacy_enrollments.values_list("course_id", flat=True)
    )
    owned_course_ids = set(
        Course.objects.filter(instructor=user.username).values_list("id", flat=True)
    ) | set(
        Course.objects.filter(instructor_user=user).values_list("id", flat=True)
    )

    all_active_ids = active_course_ids | legacy_course_ids | owned_course_ids
    total_active = len(all_active_ids)
    has_any_access = total_active > 0

    context = {
        "marketplace_enrollments": marketplace_enrollments,
        "legacy_enrollments": legacy_enrollments,
        "total_active": total_active,
        "has_any_access": has_any_access,
    }
    return render(request, "marketplace/access_restricted.html", context)


def _is_instructor(user) -> bool:
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
    user = request.user

    if not _is_instructor(user):
        messages.error(request, "Access denied. This page is for instructors only.")
        return redirect("courses:courses")

    wallet, _ = InstructorWallet.objects.get_or_create(
        instructor=user,
        defaults={"balance": Decimal("0.00")},
    )

    transactions = (
        WalletTransaction.objects.filter(wallet=wallet)
        .order_by("-created_at")[:50]
    )

    instructor_courses = Course.objects.filter(instructor_user=user)

    course_stats = []
    for course in instructor_courses:
        student_count = (
            Enrollment.objects.filter(course=course, is_active=True)
            .values("student").distinct().count()
        )
        course_stats.append(
            {
                "course": course,
                "student_count": student_count,
            }
        )

    withdrawal_requests = WithdrawalRequest.objects.filter(wallet=wallet).order_by(
        "-created_at"
    )[:20]

    total_withdrawn = (
        WithdrawalRequest.objects.filter(
            wallet=wallet, status=WithdrawalRequest.Status.APPROVED
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

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


@login_required
def my_courses_page(request):
    user = request.user
    is_instructor = _is_instructor(user)

    if request.method == "POST" and request.POST.get("action") == "apply_code":
        course_id = request.POST.get("course_id")
        code = request.POST.get("code", "").strip()
        try:
            course = get_object_or_404(Course, id=int(course_id))
            if is_course_owner(user, course):
                messages.info(request, f"أنت صاحب كورس '{course.title}'، لديك وصول كامل تلقائياً.")
            else:
                MarketplaceService.activate_enrollment_code(
                    user=user, course=course, code=code
                )
                messages.success(request, f"Enrolled in '{course.title}' successfully!")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect(request.path)

    if is_instructor:
        owned_by_username = Course.objects.filter(instructor=user.username)
        owned_by_fk = Course.objects.filter(instructor_user=user)
        instructor_course_ids = set(
            list(owned_by_username.values_list('id', flat=True)) +
            list(owned_by_fk.values_list('id', flat=True))
        )
        instructor_courses = Course.objects.filter(id__in=instructor_course_ids).order_by("-created_at")

        course_data = []
        for course in instructor_courses:
            mp_students = (
                Enrollment.objects.filter(course=course, is_active=True)
                .values("student").distinct().count()
            )
            legacy_students = (
                CourseEnrollment.objects.filter(course=course)
                .values("user").distinct().count()
            )
            total_students = max(mp_students, legacy_students)
            course_data.append(
                {
                    "course": course,
                    "student_count": total_students,
                    "is_owner": True,
                }
            )

        context = {
            "is_instructor": True,
            "course_data": course_data,
        }

    else:
        marketplace_enrollments = (
            Enrollment.objects.filter(student=user, is_active=True)
            .select_related("course")
            .order_by("-enrolled_at")
        )

        legacy_enrollments = (
            CourseEnrollment.objects.filter(user=user)
            .select_related("course")
            .order_by("-enrolled_at")
        )

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
                        "is_owner": False,
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
                        "is_owner": False,
                    }
                )

        context = {
            "is_instructor": False,
            "enrollments": combined_enrollments,
        }

    return render(request, "marketplace/my_courses.html", context)