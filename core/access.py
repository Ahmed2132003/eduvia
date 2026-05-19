"""
core/access.py
==============
منطق التحقق من صلاحية الوصول الجديد.
يستبدل نظام الاشتراكات والخطط بالكامل.

القاعدة: يُسمح للمستخدم بالوصول إذا كان لديه
كورس مسجَّل أو نشط خلال آخر 60 يومًا.
"""

from datetime import timedelta
from django.utils.timezone import now

# ── استيراد على مستوى الـ module حتى يعمل patch في الاختبارات ──
try:
    from courses.models import CourseEnrollment
except ImportError:
    CourseEnrollment = None

try:
    from courses.models import VideoProgress
except ImportError:
    VideoProgress = None

# ── ثوابت ──
COURSE_ACCESS_DAYS = 60

ACCESS_DENIED_MESSAGE = (
    "يجب الاشتراك في كورس واحد على الأقل خلال آخر 60 يومًا لاستخدام هذه الخدمة."
)


def has_recent_course_access(user) -> bool:
    """
    يرجع True إذا كان المستخدم لديه كورس صالح خلال آخر 60 يومًا.
    يفحص: CourseEnrollment ثم VideoProgress.
    """
    if not user or not user.is_authenticated:
        return False

    # superuser / staff دائمًا مسموح لهم
    if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
        return True

    cutoff = now() - timedelta(days=COURSE_ACCESS_DAYS)

    # ── فحص CourseEnrollment ──
    if CourseEnrollment is not None:
        try:
            # محاولة الفلتر بتاريخ التسجيل
            if CourseEnrollment.objects.filter(
                user=user,
                enrolled_at__gte=cutoff
            ).exists():
                return True
        except Exception:
            # حقل enrolled_at غير موجود → أي تسجيل يكفي
            try:
                if CourseEnrollment.objects.filter(user=user).exists():
                    return True
            except Exception:
                pass

    # ── فحص VideoProgress ──
    if VideoProgress is not None:
        try:
            if VideoProgress.objects.filter(
                user=user,
                last_watched__gte=cutoff
            ).exists():
                return True
        except Exception:
            pass

    return False


def can_access_performance_analysis(user) -> bool:
    return has_recent_course_access(user)


def can_access_projects(user) -> bool:
    return has_recent_course_access(user)


def can_access_skills_market(user) -> bool:
    return has_recent_course_access(user)


def can_access_workshops(user) -> bool:
    return has_recent_course_access(user)