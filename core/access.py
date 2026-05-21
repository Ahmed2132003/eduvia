

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


def _is_instructor_owner(user) -> bool:
    """
    يُرجع True إذا كان المستخدم instructor ويملك كورساً واحداً على الأقل.
    يُمنح وصولاً فورياً دون الحاجة لفحص التاريخ.
    """
    try:
        from courses.models import Course
        if Course.objects.filter(instructor=user.username).exists():
            return True
        if Course.objects.filter(instructor_user=user).exists():
            return True
    except Exception:
        pass
    return False


def has_recent_course_access(user) -> bool:
    """
    يرجع True إذا كان المستخدم لديه كورس صالح خلال آخر 60 يومًا.
    يفحص (بالترتيب):
      1. superuser / staff → True دائماً
      2. Instructor صاحب كورس → True دائماً
      3. CourseEnrollment في آخر 60 يوم
      4. Marketplace Enrollment نشط
      5. VideoProgress في آخر 60 يوم
    """
    if not user or not user.is_authenticated:
        return False

    # ── 1. superuser / staff دائمًا مسموح لهم ──
    if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
        return True

    # ── 2. Instructor owner — وصول فوري ──
    if _is_instructor_owner(user):
        return True

    cutoff = now() - timedelta(days=COURSE_ACCESS_DAYS)

    # ── 3. فحص CourseEnrollment ──
    if CourseEnrollment is not None:
        try:
            if CourseEnrollment.objects.filter(
                user=user,
                enrolled_at__gte=cutoff,
            ).exists():
                return True
        except Exception:
            try:
                if CourseEnrollment.objects.filter(user=user).exists():
                    return True
            except Exception:
                pass

    # ── 4. فحص Marketplace Enrollment ──
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

    # ── 5. فحص VideoProgress ──
    if VideoProgress is not None:
        try:
            if VideoProgress.objects.filter(
                user=user,
                last_watched__gte=cutoff,
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
