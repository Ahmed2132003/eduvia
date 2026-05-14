from django.shortcuts import redirect
from django.urls import resolve
from .models import Enrollment

EXEMPT_NAMES = {
    'pages:home',
    'courses:courses',
    'accounts:login',
    'accounts:register',
}


class StudentAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'courses_profile'):
            profile = request.user.courses_profile
            if profile.role == 'student':
                enrolled = Enrollment.objects.filter(student=request.user, is_active=True).exists()
                name = resolve(request.path_info).view_name
                if not enrolled and name not in EXEMPT_NAMES and not request.path.startswith('/api/marketplace/student/'):
                    return redirect('/courses/')
        return self.get_response(request)