
from django.utils import timezone
from datetime import timedelta


def _get_cutoff_date():
    """إرجاع تاريخ الحد (آخر 60 يوم)"""
    return timezone.now() - timedelta(days=60)


def is_instructor_with_course(user) -> bool:
    """
    يُرجع True إذا كان المستخدم instructor ويملك كورساً واحداً على الأقل.
    هذا يمنحه وصولاً تلقائياً للشات بوت والمسابقات.
    """
    if not user or not user.is_authenticated:
        return False

    try:
        from courses.models import Course
        return Course.objects.filter(instructor=user.username).exists()
    except Exception:
        pass

    try:
        from courses.models import Course
        return Course.objects.filter(instructor_user=user).exists()
    except Exception:
        pass

    return False


def has_active_course_access(user):
    """
    التحقق هل لدى المستخدم كورس صالح خلال آخر 60 يوم.
    يبحث في:
    - CourseEnrollment (التسجيل في كورس)
    - Purchase (شراء كورس)
    - CourseAccess (وصول مباشر للكورس)
    - Instructor ownership (صاحب الكورس دائماً مؤهل)

    يُرجع True إذا وُجد أي منها، وإلا False.
    """
    if not user or not user.is_authenticated:
        return False

    # Superusers لديهم وصول دائم
    if user.is_superuser:
        return True

    # ---- Instructor Owner: دائماً مؤهل إذا كان صاحب كورس ----
    if is_instructor_with_course(user):
        return True

    cutoff = _get_cutoff_date()

    # ---- CourseEnrollment ----
    try:
        from courses.models import CourseEnrollment
        if CourseEnrollment.objects.filter(
            user=user,
            enrolled_at__gte=cutoff
        ).exists():
            return True
    except Exception:
        pass

    # ---- Marketplace Enrollment ----
    try:
        from marketplace.models import Enrollment as MarketplaceEnrollment
        if MarketplaceEnrollment.objects.filter(
            student=user,
            is_active=True,
            enrolled_at__gte=cutoff,
        ).exists():
            return True
    except Exception:
        pass

    # ---- Purchase / Order ----
    try:
        from courses.models import Purchase
        if Purchase.objects.filter(
            user=user,
            purchased_at__gte=cutoff
        ).exists():
            return True
    except Exception:
        pass

    # ---- CourseAccess ----
    try:
        from courses.models import CourseAccess
        if CourseAccess.objects.filter(
            user=user,
            granted_at__gte=cutoff
        ).exists():
            return True
    except Exception:
        pass

    # ---- UserCourse (اسم بديل شائع) ----
    try:
        from courses.models import UserCourse
        if UserCourse.objects.filter(
            user=user,
            created_at__gte=cutoff
        ).exists():
            return True
    except Exception:
        pass

    return False


def can_access_chatbot(user):
    """
    هل يمكن للمستخدم استخدام الشات بوت؟
    يُرجع True إذا كان لديه كورس صالح خلال آخر 60 يوم
    أو كان instructor صاحب كورس.
    """
    return has_active_course_access(user)


def can_access_competitions(user):
    """
    هل يمكن للمستخدم المشاركة في المسابقات؟
    يُرجع True إذا كان لديه كورس صالح خلال آخر 60 يوم
    أو كان instructor صاحب كورس.
    """
    return has_active_course_access(user)


# رسالة الرفض الموحدة
ACCESS_DENIED_MESSAGE = (
    "يجب الاشتراك في كورس واحد على الأقل خلال آخر شهرين "
    "لاستخدام الشات بوت أو الدخول للمسابقات."
)

ACCESS_DENIED_RESPONSE = {
    "detail": ACCESS_DENIED_MESSAGE
}
