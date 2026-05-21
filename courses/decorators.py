"""
courses/decorators.py
=====================
Role-Based Access Control decorators for the courses app.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def instructor_required(view_func):
    """
    Decorator that restricts access to instructor-only views.

    Rules:
    - Unauthenticated users → redirect to login.
    - Authenticated students (role != 'instructor') → redirect to
      the dedicated 'access_denied' page.
    - Superusers are always allowed through.
    - Instructors pass through normally.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 1. Must be logged in
        if not request.user.is_authenticated:
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

        # 5. Student (or any non-instructor) → access denied page
        return redirect('courses:access_denied')

    return wrapper