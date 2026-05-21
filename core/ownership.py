from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from courses.models import Course


def is_course_owner(user: "AbstractBaseUser", course: "Course") -> bool:
    """
    Return True if *user* is the owner / instructor of *course*.

    This check is intentionally kept pure (no DB queries beyond what
    the caller already loaded) and is safe to call from any layer:
    views, decorators, serializers, API permissions, templates, etc.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False

    # ── 1. Superuser always wins ──────────────────────────────────────────────
    if getattr(user, "is_superuser", False):
        return True

    # ── 2. Legacy string field: course.instructor == username ─────────────────
    course_instructor_name = getattr(course, "instructor", None)
    if course_instructor_name and course_instructor_name == user.username:
        return True

    # ── 3. FK field: course.instructor_user == user ───────────────────────────
    instructor_user_id = getattr(course, "instructor_user_id", None)
    if instructor_user_id and instructor_user_id == user.pk:
        return True

    # Also handle the case where instructor_user is already loaded as object
    instructor_user_obj = getattr(course, "instructor_user", None)
    if instructor_user_obj is not None and hasattr(instructor_user_obj, "pk"):
        if instructor_user_obj.pk == user.pk:
            return True

    return False


def has_full_course_access(user: "AbstractBaseUser", course: "Course") -> bool:
    """
    Return True if the user should bypass the purchase/enrollment gate.

    Currently equivalent to is_course_owner, but kept as a separate
    function so future roles (e.g. TA, co-instructor, admin) can be
    added here without touching every call-site.
    """
    return is_course_owner(user, course)
