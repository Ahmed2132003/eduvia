from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .serializers import BuyCourseSerializer, ApplyCodeSerializer, CoursePurchaseSerializer, EnrollmentSerializer
from .models import CoursePurchase, Enrollment, InstructorWallet
from .services import MarketplaceService
from courses.models import Course


class BuyCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = BuyCourseSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        course = Course.objects.get(id=data.validated_data['course_id'])
        purchase, _ = CoursePurchase.objects.get_or_create(
            idempotency_key=data.validated_data['idempotency_key'],
            defaults={'student': request.user, 'course': course, 'amount': course.price, 'currency': 'EGP'},
        )
        return Response(CoursePurchaseSerializer(purchase).data)


class ApplyEnrollmentCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = ApplyCodeSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        enrollment = MarketplaceService.apply_enrollment_code(student=request.user, course_id=data.validated_data['course_id'], code_value=data.validated_data['code'])
        return Response(EnrollmentSerializer(enrollment).data)


class MyCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course')
        return Response(EnrollmentSerializer(enrollments, many=True).data)


class InstructorEarningsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = request.user.wallet.transactions.filter(tx_type='revenue').aggregate(total=Sum('amount'))['total'] or 0
        return Response({'total_earnings': total})


@login_required
def checkout_page(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'marketplace/checkout.html', {'courses': courses})


@login_required
def my_courses_page(request):
    if request.method == 'POST' and request.POST.get('action') == 'apply_code':
        try:
            MarketplaceService.apply_enrollment_code(
                student=request.user,
                course_id=int(request.POST.get('course_id')),
                code_value=request.POST.get('code', '').strip(),
            )
            messages.success(request, 'Enrollment code applied successfully.')
        except Exception as exc:
            messages.error(request, f'Failed to apply enrollment code: {exc}')
        return redirect('marketplace_my_courses')

    enrollments = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course')
    return render(request, 'marketplace/my_courses.html', {'enrollments': enrollments})


@login_required
def access_restricted_page(request):
    return render(request, 'marketplace/access_restricted.html')


@login_required
def instructor_wallet_page(request):
    wallet, _ = InstructorWallet.objects.get_or_create(instructor=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')[:20]
    return render(request, 'marketplace/instructor_wallet.html', {'wallet': wallet, 'transactions': transactions})