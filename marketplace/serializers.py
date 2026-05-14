from rest_framework import serializers
from .models import CoursePurchase, EnrollmentCode, Enrollment, WithdrawalRequest


class BuyCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    idempotency_key = serializers.CharField(max_length=128)


class ApplyCodeSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    code = serializers.CharField(max_length=64)


class CoursePurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePurchase
        fields = ['id', 'course', 'amount', 'currency', 'status', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['course', 'source', 'created_at']


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'amount', 'status', 'created_at']