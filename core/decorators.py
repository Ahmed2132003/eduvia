"""
core/decorators.py
==================
ديكوراتور للتحقق من صلاحية الوصول بناءً على المنطق الجديد.
"""

from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from .access import ACCESS_DENIED_MESSAGE


def require_course_access(checker_fn):
    """
    ديكوراتور مصنع يقبل دالة الفحص المناسبة.

    الاستخدام:
        from core.access import can_access_projects
        from core.decorators import require_course_access

        @login_required
        @require_course_access(can_access_projects)
        def my_view(request):
            ...

    - إذا كان الطلب JSON/API يُرجع 403 JSON.
    - إذا كان طلب HTML يُضيف رسالة خطأ ويُعيد redirect للصفحة الرئيسية.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if _is_api_request(request):
                    return JsonResponse(
                        {"detail": ACCESS_DENIED_MESSAGE}, status=403
                    )
                return redirect('/accounts/login/')

            if not checker_fn(request.user):
                if _is_api_request(request):
                    return JsonResponse(
                        {"detail": ACCESS_DENIED_MESSAGE}, status=403
                    )
                messages.error(request, ACCESS_DENIED_MESSAGE)
                return redirect('/')

            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def _is_api_request(request) -> bool:
    """يكتشف ما إذا كان الطلب API أو HTML."""
    accept = request.META.get('HTTP_ACCEPT', '')
    content_type = request.META.get('CONTENT_TYPE', '')
    return (
        'application/json' in accept
        or 'application/json' in content_type
        or request.path.startswith('/api/')
    )