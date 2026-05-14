from django.shortcuts import redirect

from .models import Enrollment


class StudentAccessMiddleware:
    ALLOWED_PREFIXES = (
        "/",
        "/courses/",
        "/accounts/login/",
        "/accounts/register/",
        "/api/marketplace/courses/",
        "/api/marketplace/payments/webhook/",
        "/api/marketplace/my/access-status/",
        "/api/marketplace/my/enrollments/",
        "/api/marketplace/checkout/",
        "/api/marketplace/access-restricted/",
        "/admin/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and getattr(user, "role", None) == "student":
            if not Enrollment.objects.filter(student=user, is_active=True).exists():
                path = request.path
                if not any(path.startswith(prefix) for prefix in self.ALLOWED_PREFIXES):
                    return redirect("marketplace_access_restricted")
        return self.get_response(request)