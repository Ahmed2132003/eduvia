"""
courses/decorators.py
=====================
Role-Based Access Control decorators for the courses app.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


def _is_ajax(request):
    """
    Detect AJAX / JSON requests.
    curriculum_builder.js uses fetch() with Content-Type: application/json,
    so we check that header in addition to the classic XMLHttpRequest one.
    """
    return (
        'application/json' in request.headers.get('Content-Type', '')
        or 'application/json' in request.headers.get('Accept', '')
        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )


def instructor_required(view_func):
    """
    Decorator that restricts access to instructor-only views.

    Rules:
    - Unauthenticated users → redirect to login  (or JSON 403 for AJAX).
    - Authenticated students (role != 'instructor') → redirect to
      the dedicated 'access_denied' page  (or JSON 403 for AJAX).
    - Superusers are always allowed through.
    - Instructors pass through normally.

    AJAX / JSON requests ALWAYS receive a JsonResponse so that fetch()
    calls in the curriculum builder never receive an HTML redirect page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 1. Must be logged in
        if not request.user.is_authenticated:
            if _is_ajax(request):
                return JsonResponse(
                    {'ok': False, 'error': 'Authentication required.'},
                    status=403,
                )
            messages.error(request, 'You need to be logged in.')
            return redirect('accounts:login')

        # 2. Superusers bypass role checks
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # 3. Check the role on the User model (accounts.User)
        if getattr(request.user, 'role', None) == 'instructor':
            return view_func(request, *args, **kwargs)

        # 4. Fallback: check the courses UserProfile role
        try:
            if request.user.courses_profile.role == 'instructor':
                return view_func(request, *args, **kwargs)
        except Exception:
            pass

        # 5. Student (or any non-instructor) → access denied
        if _is_ajax(request):
            return JsonResponse(
                {'ok': False, 'error': 'Instructor access required.'},
                status=403,
            )
        return redirect('courses:access_denied')

    return wrapper