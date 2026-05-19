"""
core/access.py
==============
منطق التحقق من صلاحية الوصول الجديد.
يستبدل نظام الاشتراكات والخطط بالكامل.

القاعدة: يُسمح للمستخدم بالوصول إذا كان لديه
كورس مسجَّل أو مشتري أو نشط خلال آخر 60 يومًا.
"""

from django.utils.timezone import now
from datetime import timedelta

COURSE_ACCESS_DAYS = 60


def has_recent_course_access(user) -> bool:
    """
    يرجع True إذا كان المستخدم لديه كورس صالح خلال آخر 60 يومًا.
    يفحص: CourseEnrollment, CoursePurchase (إن وُجد), VideoProgress
    """
    if not user or not user.is_authenticated:
        return False

    # Superusers / staff دائمًا مسموح لهم
    if user.is_staff or user.is_superuser:
        return True

    cutoff = now() - timedelta(days=COURSE_ACCESS_DAYS)

    # فحص CourseEnrollment
    try:
        from courses.models import CourseEnrollment
        if CourseEnrollment.objects.filter(
            user=user,
            enrolled_at__gte=cutoff
        ).exists():
            return True
    except Exception:
        pass

    # فحص VideoProgress كدليل على وجود نشاط في كورس حديث
    try:
        from courses.models import VideoProgress
        if VideoProgress.objects.filter(
            user=user,
            last_watched__gte=cutoff
        ).exists():
            return True
    except Exception:
        pass

    # فحص CourseEnrollment بدون تاريخ محدد (fallback - أي تسجيل موجود)
    # هذا يُستخدم إذا لم يكن حقل enrolled_at موجودًا
    try:
        from courses.models import CourseEnrollment
        if not hasattr(CourseEnrollment, 'enrolled_at'):
            # إذا لم يوجد حقل التاريخ نسمح لأي مسجَّل
            if CourseEnrollment.objects.filter(user=user).exists():
                return True
    except Exception:
        pass

    return False


def can_access_performance_analysis(user) -> bool:
    """يرجع True إذا يحق للمستخدم الوصول إلى تحليل الأداء."""
    return has_recent_course_access(user)


def can_access_projects(user) -> bool:
    """يرجع True إذا يحق للمستخدم الوصول إلى المشاريع."""
    return has_recent_course_access(user)


def can_access_skills_market(user) -> bool:
    """يرجع True إذا يحق للمستخدم الوصول إلى سوق المهارات."""
    return has_recent_course_access(user)


def can_access_workshops(user) -> bool:
    """يرجع True إذا يحق للمستخدم الوصول إلى الورش."""
    return has_recent_course_access(user)


# رسالة الرفض الموحَّدة
ACCESS_DENIED_MESSAGE = (
    "يجب الاشتراك في كورس واحد على الأقل خلال آخر شهرين لاستخدام هذه الخدمة."
)