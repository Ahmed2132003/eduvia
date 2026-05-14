import hmac
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from .models import CoursePayment, Enrollment
from .serializers import ActivateCodeSerializer, EnrollmentSerializer, WebhookSerializer
from .services import MarketplaceService


class CheckoutPaymobAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        return Response(MarketplaceService.create_paymob_checkout(user=request.user, course=course), status=201)


class ActivateCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        serializer = ActivateCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(Course, id=course_id)
        enrollment = MarketplaceService.activate_enrollment_code(user=request.user, course=course, code=serializer.validated_data["code"])
        return Response(EnrollmentSerializer(enrollment).data)


class PaymentWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        secret = getattr(settings, "PAYMOB_HMAC_SECRET", "")
        expected = hmac.new(secret.encode(), serializer.validated_data["transaction_id"].encode(), "sha512").hexdigest()
        if not hmac.compare_digest(expected, serializer.validated_data["hmac"]):
            return Response({"detail": "invalid signature"}, status=400)
        payment = get_object_or_404(CoursePayment, transaction_id=serializer.validated_data["transaction_id"])
        MarketplaceService.finalize_payment(payment=payment, webhook_payload=serializer.validated_data["payload"])
        return Response({"status": "ok"})


class MyEnrollmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = Enrollment.objects.filter(student=request.user, is_active=True).select_related("course")
        return Response(EnrollmentSerializer(rows, many=True).data)


class AccessStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"has_access": Enrollment.objects.filter(student=request.user, is_active=True).exists()})


@login_required
def access_restricted_page(request):
    return render(request, "marketplace/access_restricted.html")


@login_required
def checkout_page(request):
    course = get_object_or_404(Course, id=request.GET.get("course_id")) if request.GET.get("course_id") else None
    return render(request, "marketplace/checkout.html", {"course": course, "courses": Course.objects.all().order_by("-created_at")[:20]})