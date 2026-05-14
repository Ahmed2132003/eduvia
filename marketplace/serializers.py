from rest_framework import serializers

from .models import CoursePayment, Enrollment


class CheckoutPaymobSerializer(serializers.Serializer):
    pass


class ActivateCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)


class WebhookSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=128)
    hmac = serializers.CharField(max_length=255)
    payload = serializers.JSONField()


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["course_id", "source", "enrolled_at", "is_active"]


class AccessStatusSerializer(serializers.Serializer):
    has_access = serializers.BooleanField()


class CoursePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePayment
        fields = ["transaction_id", "payment_status", "amount", "provider"]