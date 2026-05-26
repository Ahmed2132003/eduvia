from rest_framework import serializers

from .models import Enrollment


class ActivateCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["course_id", "source", "enrolled_at", "is_active"]


class AccessStatusSerializer(serializers.Serializer):
    has_access = serializers.BooleanField()