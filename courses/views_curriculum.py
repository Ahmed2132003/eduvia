"""
courses/views_curriculum.py
────────────────────────────────────────────────────────────────────────────────
Curriculum System — Udemy-like Section / Lesson management.

Instructor views:
  • curriculum_builder      GET/POST — AJAX-driven builder page
  • section_create          POST (AJAX)
  • section_update          POST (AJAX)
  • section_delete          POST (AJAX)
  • section_reorder         POST (AJAX)
  • lesson_create           POST (AJAX)
  • lesson_update           GET/POST
  • lesson_delete           POST (AJAX)
  • lesson_reorder          POST (AJAX)

Student views:
  • course_curriculum_view  GET  — public curriculum (enrolled students)
  • lesson_view             GET/POST — watch / read a lesson
  • lesson_progress_update  POST (AJAX) — update progress
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from core.ownership import is_course_owner, has_full_course_access
from .decorators import instructor_required
from .models import (
    Course, CourseEnrollment, Lesson, LessonProgress,
    Section, UserProfile, VideoProgress,
)
from .utils import clean_text

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _json_error(msg, status=400):
    return JsonResponse({'ok': False, 'error': msg}, status=status)


def _json_ok(data=None):
    payload = {'ok': True}
    if data:
        payload.update(data)
    return JsonResponse(payload)


def _is_enrolled(user, course):
    """Unified enrollment check (same logic as views.py)."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if has_full_course_access(user, course):
        return True
    if CourseEnrollment.objects.filter(user=user, course=course).exists():
        return True
    try:
        from marketplace.models import Enrollment as MarketplaceEnrollment
        if MarketplaceEnrollment.objects.filter(
            student=user, course=course, is_active=True
        ).exists():
            return True
    except Exception:
        pass
    return False


def _section_data(section):
    """Serialize a section + its lessons for AJAX responses."""
    return {
        'id': section.id,
        'title': section.title,
        'order': section.order,
        'lessons': [_lesson_data(l) for l in section.lessons.order_by('order')],
    }


def _lesson_data(lesson):
    return {
        'id': lesson.id,
        'title': lesson.title,
        'lesson_type': lesson.lesson_type,
        'type_label': lesson.get_type_label(),
        'icon': lesson.get_icon(),
        'order': lesson.order,
        'video_url': lesson.video_url or '',
        'video_duration': lesson.video_duration,
        'duration_display': lesson.get_duration_display(),
        'is_preview': lesson.is_preview,
        'description': lesson.description,
        'content': lesson.content,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CURRICULUM BUILDER  (Instructor)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def curriculum_builder(request, course_id, course_slug):
    """
    Main builder page — renders the Udemy-style drag-drop curriculum editor.
    All mutations happen via AJAX sub-views below.
    """
    course = get_object_or_404(Course, id=course_id)

    if not request.user.is_superuser and not is_course_owner(request.user, course):
        messages.error(request, "غير مصرح لك بتعديل منهج هذا الكورس.")
        return redirect('courses:instructor_dashboard')

    sections = course.sections.prefetch_related('lessons').order_by('order')

    context = {
        'course': course,
        'sections': sections,
        'course_slug': slugify(clean_text(course.title), allow_unicode=True) or 'default',
    }
    return render(request, 'courses/curriculum_builder.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION CRUD  (AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
@require_POST
def section_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    title = (data.get('title') or '').strip()
    if not title:
        return _json_error('Section title is required.')

    last_order = Section.objects.filter(course=course).count()
    section = Section.objects.create(
        course=course,
        title=title,
        order=last_order,
    )
    return _json_ok({'section': _section_data(section)})


@login_required
@instructor_required
@require_POST
def section_update(request, course_id, section_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    title = (data.get('title') or '').strip()
    if not title:
        return _json_error('Section title is required.')

    section.title = title
    section.save(update_fields=['title'])
    return _json_ok({'section': _section_data(section)})


@login_required
@instructor_required
@require_POST
def section_delete(request, course_id, section_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    section.delete()

    # Re-order remaining sections
    for idx, s in enumerate(Section.objects.filter(course=course).order_by('order')):
        if s.order != idx:
            s.order = idx
            s.save(update_fields=['order'])

    return _json_ok({'deleted': section_id})


@login_required
@instructor_required
@require_POST
def section_reorder(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    try:
        data = json.loads(request.body)
        ordered_ids = data.get('order', [])
    except (json.JSONDecodeError, ValueError):
        return _json_error('Invalid JSON')

    for idx, section_id in enumerate(ordered_ids):
        Section.objects.filter(id=section_id, course=course).update(order=idx)

    return _json_ok()


# ─────────────────────────────────────────────────────────────────────────────
# LESSON CRUD  (AJAX + form page for text/article)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
@require_POST
def lesson_create(request, course_id, section_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST.dict()

    title = (data.get('title') or '').strip()
    lesson_type = data.get('lesson_type', 'video')
    video_url = (data.get('video_url') or '').strip()
    video_duration = 0
    try:
        video_duration = float(data.get('video_duration', 0) or 0)
    except (ValueError, TypeError):
        video_duration = 0

    is_preview = bool(data.get('is_preview', False))
    description = (data.get('description') or '').strip()
    content = (data.get('content') or '').strip()

    if not title:
        return _json_error('Lesson title is required.')

    if lesson_type == 'video' and not video_url:
        return _json_error('Video URL is required for video lessons.')

    last_order = section.lessons.count()
    lesson = Lesson.objects.create(
        section=section,
        title=title,
        lesson_type=lesson_type,
        order=last_order,
        video_url=video_url if lesson_type == 'video' else None,
        video_duration=video_duration,
        is_preview=is_preview,
        description=description,
        content=content,
    )
    return _json_ok({'lesson': _lesson_data(lesson)})


@login_required
@instructor_required
@require_POST
def lesson_update(request, course_id, section_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, section=section)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST.dict()

    title = (data.get('title') or '').strip()
    lesson_type = data.get('lesson_type', lesson.lesson_type)
    video_url = (data.get('video_url') or '').strip()
    video_duration = lesson.video_duration
    try:
        video_duration = float(data.get('video_duration', lesson.video_duration) or 0)
    except (ValueError, TypeError):
        pass

    is_preview = bool(data.get('is_preview', lesson.is_preview))
    description = (data.get('description') or '').strip()
    content = (data.get('content') or '').strip()

    if not title:
        return _json_error('Lesson title is required.')

    if lesson_type == 'video' and not video_url:
        return _json_error('Video URL is required for video lessons.')

    lesson.title = title
    lesson.lesson_type = lesson_type
    lesson.video_url = video_url if lesson_type == 'video' else None
    lesson.video_duration = video_duration
    lesson.is_preview = is_preview
    lesson.description = description
    lesson.content = content
    lesson.save()

    return _json_ok({'lesson': _lesson_data(lesson)})


@login_required
@instructor_required
@require_POST
def lesson_delete(request, course_id, section_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, section=section)
    lesson.delete()

    # Re-order remaining lessons in this section
    for idx, l in enumerate(section.lessons.order_by('order')):
        if l.order != idx:
            l.order = idx
            l.save(update_fields=['order'])

    return _json_ok({'deleted': lesson_id})


@login_required
@instructor_required
@require_POST
def lesson_reorder(request, course_id, section_id):
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        data = json.loads(request.body)
        ordered_ids = data.get('order', [])
    except (json.JSONDecodeError, ValueError):
        return _json_error('Invalid JSON')

    for idx, lesson_id in enumerate(ordered_ids):
        Lesson.objects.filter(id=lesson_id, section=section).update(order=idx)

    return _json_ok()


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT — COURSE CURRICULUM PAGE
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def course_curriculum_view(request, course_id, course_slug):
    """
    Udemy-style curriculum page for enrolled students.
    Shows all sections + lessons with progress indicators.
    """
    course = get_object_or_404(Course, id=course_id)
    slugified = slugify(clean_text(course.title), allow_unicode=True) or 'default'

    from django.http import HttpResponsePermanentRedirect
    from django.urls import reverse
    if slugified != course_slug:
        return HttpResponsePermanentRedirect(
            reverse('courses:course_curriculum', kwargs={
                'course_id': course_id,
                'course_slug': slugified,
            })
        )

    # Enrollment / ownership check
    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)

    if not enrolled:
        messages.error(request, 'يجب شراء هذه الدورة لعرض المنهج.')
        return redirect('courses:courses')

    # Prefetch everything in 2 queries (no N+1)
    sections = course.sections.prefetch_related('lessons').order_by('order')

    # Build progress map for this user
    completed_lesson_ids = set(
        LessonProgress.objects.filter(
            user=request.user,
            lesson__section__course=course,
            completed=True,
        ).values_list('lesson_id', flat=True)
    )

    total_lessons = 0
    completed_count = 0
    sections_data = []

    for section in sections:
        lessons = list(section.lessons.order_by('order'))
        section_completed = 0
        for lesson in lessons:
            lesson.is_completed = lesson.id in completed_lesson_ids
            if lesson.is_completed:
                section_completed += 1
        total_lessons += len(lessons)
        completed_count += section_completed
        sections_data.append({
            'section': section,
            'lessons': lessons,
            'completed': section_completed,
            'total': len(lessons),
        })

    progress_pct = round((completed_count / total_lessons * 100) if total_lessons else 0)

    context = {
        'course': course,
        'sections_data': sections_data,
        'total_lessons': total_lessons,
        'completed_count': completed_count,
        'progress_pct': progress_pct,
        'is_owner': is_owner,
        'is_enrolled': enrolled,
        'course_slug': slugified,
    }
    return render(request, 'courses/course_curriculum.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT — LESSON VIEW
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_view(request, course_id, course_slug, lesson_id):
    """
    Renders a single lesson — video player OR rich-text reader.
    Also handles progress update on POST.
    """
    course = get_object_or_404(Course, id=course_id)
    slugified = slugify(clean_text(course.title), allow_unicode=True) or 'default'

    from django.http import HttpResponsePermanentRedirect
    from django.urls import reverse
    if slugified != course_slug:
        return HttpResponsePermanentRedirect(
            reverse('courses:lesson_view', kwargs={
                'course_id': course_id,
                'course_slug': slugified,
                'lesson_id': lesson_id,
            })
        )

    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)

    # Preview lessons are public even without enrollment
    if not enrolled and not lesson.is_preview:
        messages.error(request, 'يجب شراء هذه الدورة لمشاهدة هذا الدرس.')
        return redirect('courses:courses')

    # Get or create progress
    lesson_progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': False, 'progress_percentage': 0.0},
    )

    # Mark text/article lessons as complete on first view
    if lesson.lesson_type in ('text', 'article') and not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.progress_percentage = 100.0
        lesson_progress.save()

    # Sidebar: all sections + lessons with completion info
    sections = course.sections.prefetch_related('lessons').order_by('order')
    completed_ids = set(
        LessonProgress.objects.filter(
            user=request.user,
            lesson__section__course=course,
            completed=True,
        ).values_list('lesson_id', flat=True)
    )

    sidebar_sections = []
    for section in sections:
        lessons = list(section.lessons.order_by('order'))
        for l in lessons:
            l.is_completed = l.id in completed_ids
            l.is_active = l.id == lesson.id
        sidebar_sections.append({'section': section, 'lessons': lessons})

    # Prev / Next lesson
    all_lessons = [
        l
        for s in sections
        for l in s.lessons.order_by('order')
    ]
    lesson_ids = [l.id for l in all_lessons]
    current_idx = lesson_ids.index(lesson.id) if lesson.id in lesson_ids else -1
    prev_lesson = all_lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if current_idx < len(all_lessons) - 1 else None

    context = {
        'course': course,
        'lesson': lesson,
        'lesson_progress': lesson_progress,
        'sidebar_sections': sidebar_sections,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'is_owner': is_owner,
        'is_enrolled': enrolled,
        'course_slug': slugified,
    }
    return render(request, 'courses/lesson_view.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# LESSON PROGRESS  (AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def lesson_progress_update(request, lesson_id):
    """AJAX: update lesson progress (current_time, progress_pct, completed)."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course

    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)
    if not enrolled:
        return _json_error('Not enrolled', 403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = {}

    current_time = float(data.get('current_time', 0) or 0)
    duration_secs = (lesson.video_duration or 0) * 60
    progress_pct = (current_time / duration_secs * 100) if duration_secs else 0
    progress_pct = min(progress_pct, 100)
    completed = progress_pct >= 90  # mark complete at 90%

    lesson_progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
    )
    lesson_progress.current_time = current_time
    lesson_progress.progress_percentage = progress_pct
    if completed and not lesson_progress.completed:
        lesson_progress.completed = True
        # Award coins on first completion
        try:
            profile = request.user.courses_profile
            profile.add_coins(30)
        except Exception:
            pass
    lesson_progress.save()

    return _json_ok({
        'progress': round(progress_pct, 1),
        'completed': lesson_progress.completed,
    })
