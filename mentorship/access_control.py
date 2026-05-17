from django.utils import timezone
from datetime import timedelta


ACCESS_DENIED_MESSAGE = "يجب الاشتراك في كورس واحد على الأقل خلال آخر شهرين لاستخدام هذه الخدمة."
ACCESS_WINDOW_DAYS = 60


def has_recent_course_access(user) -> bool:
    """
    يرجع True إذا كان المستخدم لديه كورس صالح خلال آخر 60 يوم.
    يتحقق من: Enrollment أو Purchase أو Active Course Access.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser or user.is_staff:
        return True

    cutoff_date = timezone.now() - timedelta(days=ACCESS_WINDOW_DAYS)

    try:
        from courses.models import Enrollment, Purchase, CourseAccess
        # التحقق من Enrollment
        if Enrollment.objects.filter(
            user=user,
            enrolled_at__gte=cutoff_date
        ).exists():
            return True

        # التحقق من Purchase
        if Purchase.objects.filter(
            user=user,
            purchased_at__gte=cutoff_date
        ).exists():
            return True

        # التحقق من CourseAccess
        if CourseAccess.objects.filter(
            user=user,
            granted_at__gte=cutoff_date
        ).exists():
            return True

    except Exception:
        # إذا لم تكن النماذج موجودة، جرب النماذج البديلة
        pass

    # محاولة بديلة عبر UserProfile إذا كان يحمل بيانات enrollment
    try:
        from courses.models import UserProfile
        profile = UserProfile.objects.filter(user=user).first()
        if profile:
            # التحقق عبر الكورسات المسجل فيها
            if hasattr(profile, 'enrolled_courses'):
                if profile.enrolled_courses.filter(
                    enrollment__enrolled_at__gte=cutoff_date
                ).exists():
                    return True
    except Exception:
        pass

    # محاولة أخيرة: UserCourseEnrollment أو أي نموذج مشابه
    try:
        from django.apps import apps
        # البحث عن أي نموذج Enrollment في أي تطبيق
        for model in apps.get_models():
            model_name = model.__name__.lower()
            if 'enrollment' in model_name or 'enrolment' in model_name:
                fields = [f.name for f in model._meta.get_fields()]
                user_field = next(
                    (f for f in fields if f in ('user', 'student', 'learner')),
                    None
                )
                date_field = next(
                    (f for f in fields if 'date' in f or 'at' in f or 'time' in f),
                    None
                )
                if user_field and date_field:
                    try:
                        if model.objects.filter(
                            **{user_field: user, f"{date_field}__gte": cutoff_date}
                        ).exists():
                            return True
                    except Exception:
                        pass
    except Exception:
        pass

    return False


def can_access_mentorship(user) -> bool:
    """
    يرجع True إذا كان المستخدم مؤهلاً للوصول لخدمات Mentorship.
    المعيار: كورس واحد على الأقل خلال آخر 60 يوم.
    """
    return has_recent_course_access(user)


def can_access_protected_features(user) -> bool:
    """
    يرجع True إذا كان المستخدم مؤهلاً للوصول للميزات المحمية في Accounts.
    المعيار: كورس واحد على الأقل خلال آخر 60 يوم.
    """
    return has_recent_course_access(user)
