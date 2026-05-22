"""
courses/views_curriculum.py
────────────────────────────────────────────────────────────────────────────────
Curriculum System — Udemy-like Section / Lesson management.

Instructor views:
  • curriculum_builder      GET  — AJAX-driven builder page
  • section_create          POST (AJAX) → always returns JSON
  • section_update          POST (AJAX) → always returns JSON
  • section_delete          POST (AJAX) → always returns JSON
  • section_reorder         POST (AJAX) → always returns JSON
  • lesson_create           POST (AJAX) → always returns JSON
  • lesson_update           POST (AJAX) → always returns JSON
  • lesson_delete           POST (AJAX) → always returns JSON
  • lesson_reorder          POST (AJAX) → always returns JSON

Student views:
  • course_curriculum_view  GET  — public curriculum (enrolled students)
  • lesson_view             GET/POST — watch / read a lesson
  • lesson_progress_update  POST (AJAX)
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
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
    """Unified enrollment check."""
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


def _parse_body(request):
    """
    Parse JSON body safely. Falls back to request.POST dict.
    Always returns a dict — never raises.
    """
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return dict(request.POST)


def _section_data(section):
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
# CURRICULUM BUILDER  (Instructor — page render)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def curriculum_builder(request, course_id, course_slug):
    """
    Main builder page — renders the drag-drop curriculum editor.
    All mutations happen via AJAX sub-views below.
    """
    course = get_object_or_404(Course, id=course_id)

    if not request.user.is_superuser and not is_course_owner(request.user, course):
        messages.error(request, "غير مصرح لك بتعديل منهج هذا الكورس.")
        return redirect('courses:instructor_dashboard')

    sections = course.sections.prefetch_related('lessons').order_by('order')
    course_slug_clean = slugify(clean_text(course.title), allow_unicode=True) or 'default'

    context = {
        'course': course,
        'sections': sections,
        'course_slug': course_slug_clean,
    }
    return render(request, 'courses/curriculum_builder.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION CRUD  (AJAX — all return JSON)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def section_create(request, course_id):
    """
    POST /courses/instructor/curriculum/<course_id>/section/create/
    Body: { "title": "Section Name" }
    Returns: { "ok": true, "section": { ... } }

    NOTE: @require_POST is intentionally NOT used here because the fetch()
    call from curriculum_builder.js sends Content-Type: application/json,
    and some proxy/middleware combos mis-classify the method.
    We enforce POST ourselves so we can always return JSON on method errors.
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    data = _parse_body(request)
    title = str(data.get('title') or '').strip()

    if not title:
        return _json_error('Section title is required.')

    last_order = Section.objects.filter(course=course).count()
    section = Section.objects.create(
        course=course,
        title=title,
        order=last_order,
    )
    logger.info(
        "section_create: course=%s section=%s title=%r user=%s",
        course_id, section.id, title, request.user,
    )
    return _json_ok({'section': _section_data(section)})


@login_required
@instructor_required
def section_update(request, course_id, section_id):
    """POST /courses/instructor/curriculum/<course_id>/section/<section_id>/update/"""
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    data = _parse_body(request)
    title = str(data.get('title') or '').strip()

    if not title:
        return _json_error('Section title is required.')

    section.title = title
    section.save(update_fields=['title'])
    return _json_ok({'section': _section_data(section)})


@login_required
@instructor_required
def section_delete(request, course_id, section_id):
    """POST /courses/instructor/curriculum/<course_id>/section/<section_id>/delete/"""
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

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
def section_reorder(request, course_id):
    """POST /courses/instructor/curriculum/<course_id>/section/reorder/"""
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    data = _parse_body(request)
    ordered_ids = data.get('order', [])

    if not isinstance(ordered_ids, list):
        return _json_error('Invalid payload — expected {"order": [...]}')

    for idx, sid in enumerate(ordered_ids):
        try:
            Section.objects.filter(id=int(sid), course=course).update(order=idx)
        except (ValueError, TypeError):
            pass

    return _json_ok()


# ─────────────────────────────────────────────────────────────────────────────
# LESSON CRUD  (AJAX — all return JSON)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def lesson_create(request, course_id, section_id):
    """
    POST /courses/instructor/curriculum/<course_id>/section/<section_id>/lesson/create/

    Optional field: existing_video_id
      If provided, pre-fills title / video_url / video_duration from the
      matching legacy Video.  Caller may still override title, is_preview, desc.
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    from .models import Video  # local to avoid circular

    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    data = _parse_body(request)

    # ── Optional: pull data from an existing Video ────────────────────────
    existing_video_id = data.get('existing_video_id')
    legacy_video = None
    if existing_video_id:
        try:
            legacy_video = Video.objects.get(id=int(existing_video_id), course=course)
        except (Video.DoesNotExist, ValueError, TypeError):
            return _json_error('الفيديو المحدد غير موجود في هذا الكورس.')

    # ── Field resolution ──────────────────────────────────────────────────
    title = str(data.get('title') or (legacy_video.title if legacy_video else '')).strip()
    lesson_type = str(data.get('lesson_type') or 'video')

    if legacy_video:
        video_url = legacy_video.video_url or ''
        try:
            video_duration = float(legacy_video.duration) if legacy_video.duration else 0
        except (ValueError, TypeError):
            video_duration = 0
    else:
        video_url = str(data.get('video_url') or '').strip()
        try:
            video_duration = float(data.get('video_duration') or 0)
        except (ValueError, TypeError):
            video_duration = 0

    is_preview = bool(data.get('is_preview', False))
    description = str(
        data.get('description') or (legacy_video.description if legacy_video else '')
    ).strip()
    content = str(data.get('content') or '').strip()

    # ── Validation ────────────────────────────────────────────────────────
    if not title:
        return _json_error('Lesson title is required.')
    if lesson_type == 'video' and not video_url:
        return _json_error('Video URL is required for video lessons.')
    if lesson_type != 'video' and not content:
        return _json_error('Content is required for text/article lessons.')

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
def lesson_update(request, course_id, section_id, lesson_id):
    """POST /courses/instructor/curriculum/<course_id>/section/<section_id>/lesson/<lesson_id>/update/"""
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    lesson  = get_object_or_404(Lesson, id=lesson_id, section=section)
    data = _parse_body(request)

    title       = str(data.get('title') or '').strip()
    lesson_type = str(data.get('lesson_type') or lesson.lesson_type)
    video_url   = str(data.get('video_url') or '').strip()
    is_preview  = bool(data.get('is_preview', lesson.is_preview))
    description = str(data.get('description') or '').strip()
    content     = str(data.get('content') or '').strip()

    try:
        video_duration = float(data.get('video_duration') or lesson.video_duration or 0)
    except (ValueError, TypeError):
        video_duration = lesson.video_duration

    if not title:
        return _json_error('Lesson title is required.')
    if lesson_type == 'video' and not video_url:
        return _json_error('Video URL is required for video lessons.')

    lesson.title         = title
    lesson.lesson_type   = lesson_type
    lesson.video_url     = video_url if lesson_type == 'video' else None
    lesson.video_duration = video_duration
    lesson.is_preview    = is_preview
    lesson.description   = description
    lesson.content       = content
    lesson.save()

    return _json_ok({'lesson': _lesson_data(lesson)})


@login_required
@instructor_required
def lesson_delete(request, course_id, section_id, lesson_id):
    """POST /courses/instructor/curriculum/<course_id>/section/<section_id>/lesson/<lesson_id>/delete/"""
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    course  = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    lesson  = get_object_or_404(Lesson, id=lesson_id, section=section)
    lesson.delete()

    for idx, l in enumerate(section.lessons.order_by('order')):
        if l.order != idx:
            l.order = idx
            l.save(update_fields=['order'])

    return _json_ok({'deleted': lesson_id})


@login_required
@instructor_required
def lesson_reorder(request, course_id, section_id):
    """POST /courses/instructor/curriculum/<course_id>/section/<section_id>/lesson/reorder/"""
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    course  = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)

    section = get_object_or_404(Section, id=section_id, course=course)
    data = _parse_body(request)
    ordered_ids = data.get('order', [])

    if not isinstance(ordered_ids, list):
        return _json_error('Invalid payload — expected {"order": [...]}')

    for idx, lid in enumerate(ordered_ids):
        try:
            Lesson.objects.filter(id=int(lid), section=section).update(order=idx)
        except (ValueError, TypeError):
            pass

    return _json_ok()


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT — COURSE CURRICULUM PAGE
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def course_curriculum_view(request, course_id, course_slug):
    """Udemy-style curriculum page for enrolled students."""
    course = get_object_or_404(Course, id=course_id)
    slugified = slugify(clean_text(course.title), allow_unicode=True) or 'default'

    if slugified != course_slug:
        return HttpResponsePermanentRedirect(
            reverse('courses:course_curriculum', kwargs={
                'course_id': course_id,
                'course_slug': slugified,
            })
        )

    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)

    if not enrolled:
        messages.error(request, 'يجب شراء هذه الدورة لعرض المنهج.')
        return redirect('courses:courses')

    sections = course.sections.prefetch_related('lessons').order_by('order')

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
    """Renders a single lesson — video player OR rich-text reader."""
    course = get_object_or_404(Course, id=course_id)
    slugified = slugify(clean_text(course.title), allow_unicode=True) or 'default'
 
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
 
    if not enrolled and not lesson.is_preview:
        messages.error(request, 'يجب شراء هذه الدورة لمشاهدة هذا الدرس.')
        return redirect('courses:courses')
 
    # ── Lesson Progress ───────────────────────────────────────────────────────
    lesson_progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': False, 'progress_percentage': 0.0},
    )
 
    # Text / Article auto-complete
    if lesson.lesson_type in ('text', 'article') and not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.progress_percentage = 100.0
        lesson_progress.save()
 
    # ── Sidebar data ──────────────────────────────────────────────────────────
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
        lessons_qs = list(section.lessons.order_by('order'))
        for l in lessons_qs:
            l.is_completed = l.id in completed_ids
            l.is_active = l.id == lesson.id
        sidebar_sections.append({'section': section, 'lessons': lessons_qs})
 
    # ── Prev / Next ────────────────────────────────────────────────────────────
    all_lessons = [l for s in sections for l in s.lessons.order_by('order')]
    lesson_ids  = [l.id for l in all_lessons]
    current_idx = lesson_ids.index(lesson.id) if lesson.id in lesson_ids else -1
    prev_lesson = all_lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if current_idx < len(all_lessons) - 1 else None
 
    # ── Comments (new LessonComment model) ────────────────────────────────────
    from .models import LessonComment, LessonAttachment
    comments = LessonComment.objects.filter(lesson=lesson).select_related('user')[:50]
 
    # ── Attachments ────────────────────────────────────────────────────────────
    attachments = LessonAttachment.objects.filter(lesson=lesson).select_related('user')
 
    context = {
        'course':          course,
        'lesson':          lesson,
        'lesson_progress': lesson_progress,
        'sidebar_sections': sidebar_sections,
        'completed_ids':   completed_ids,        # ← set of lesson IDs completed
        'prev_lesson':     prev_lesson,
        'next_lesson':     next_lesson,
        'is_owner':        is_owner,
        'is_enrolled':     enrolled,
        'course_slug':     slugified,
        # New features
        'comments':        comments,
        'attachments':     attachments,
    }
    return render(request, 'courses/lesson_view.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# LESSON PROGRESS  (AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_progress_update(request, lesson_id):
    """
    AJAX: update lesson video progress.
    
    Request body: { "current_time": float (seconds) }
    
    Returns: {
        ok: bool,
        progress: float (0-100),
        completed: bool,
        threshold_reached: bool,   ← true when ≥85% watched
    }
    
    Anti-cheat rules (enforced server-side):
    - Progress percentage cannot decrease if already higher (no rewind exploit).
    - Completion only triggered at ≥90% — frontend shows button at 85%.
    - current_time > duration is capped at duration.
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
 
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course
 
    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)
    if not enrolled:
        return _json_error('Not enrolled', 403)
 
    data = _parse_body(request)
    try:
        current_time = float(data.get('current_time') or 0)
    except (ValueError, TypeError):
        current_time = 0
 
    # Duration in seconds
    duration_secs = (lesson.video_duration or 0) * 60
    if duration_secs > 0:
        # Cap time at duration
        current_time = min(current_time, duration_secs)
        raw_pct = (current_time / duration_secs) * 100
    else:
        raw_pct = 0
 
    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
    )
 
    # Anti-cheat: never allow progress to be sent backwards
    # (skip attack: attacker refreshes page mid-video repeatedly at 0%)
    if raw_pct < lesson_progress.progress_percentage and not created:
        # Ignore the update — return existing state
        return _json_ok({
            'progress': round(lesson_progress.progress_percentage, 1),
            'completed': lesson_progress.completed,
            'threshold_reached': lesson_progress.progress_percentage >= 85,
        })
 
    # Update progress
    lesson_progress.current_time = current_time
    lesson_progress.progress_percentage = raw_pct
    threshold_reached = raw_pct >= 85
 
    # Auto-complete at 90%
    newly_completed = False
    if raw_pct >= 90 and not lesson_progress.completed:
        lesson_progress.completed = True
        newly_completed = True
        # Award coins on first completion
        try:
            request.user.courses_profile.add_coins(30)
        except Exception:
            pass
 
    lesson_progress.save()
 
    return _json_ok({
        'progress':          round(raw_pct, 1),
        'completed':         lesson_progress.completed,
        'threshold_reached': threshold_reached,
        'newly_completed':   newly_completed,
    })


@login_required
def lesson_comment_add(request, lesson_id):
    """
    POST /courses/lesson/<lesson_id>/comment/
    Body: JSON { "content": "..." }  OR  form POST
    Returns: JSON { ok, comment: { id, user, content, created_at } }
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
 
    from .models import LessonComment, Lesson as _Lesson
    lesson = get_object_or_404(_Lesson, id=lesson_id)
 
    # enrollment check
    if not _is_enrolled(request.user, lesson.section.course) and not has_full_course_access(request.user, lesson.section.course):
        return _json_error('Not enrolled.', 403)
 
    data = _parse_body(request)
    content = str(data.get('content') or '').strip()
    if not content:
        return _json_error('Comment content is required.')
    if len(content) > 2000:
        return _json_error('Comment too long (max 2000 chars).')
 
    comment = LessonComment.objects.create(
        lesson=lesson,
        user=request.user,
        content=content,
    )
    return _json_ok({
        'comment': {
            'id': comment.id,
            'user': request.user.get_full_name() or request.user.username,
            'username': request.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%b %d, %Y'),
        }
    })
 
 
@login_required
def lesson_comment_delete(request, lesson_id, comment_id):
    """
    POST /courses/lesson/<lesson_id>/comment/<comment_id>/delete/
    Only the comment author or a superuser can delete.
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
 
    from .models import LessonComment
    comment = get_object_or_404(LessonComment, id=comment_id, lesson_id=lesson_id)
 
    if comment.user != request.user and not request.user.is_superuser:
        return _json_error('Permission denied.', 403)
 
    comment.delete()
    return _json_ok({'deleted': comment_id})
 
 
# ─────────────────────────────────────────────────────────────────────────────
# LESSON RATINGS  (AJAX)
# ─────────────────────────────────────────────────────────────────────────────
 
@login_required
def lesson_rate(request, lesson_id):
    """
    POST /courses/lesson/<lesson_id>/rate/
    Body: JSON { "rating": 4 }
    Returns: JSON {
        ok, your_rating, avg_rating, total_ratings,
        already_rated (bool), updated (bool)
    }
 
    Rules:
    - Must be enrolled (or owner).
    - rating must be integer 1-5.
    - A user can update their rating (not frozen).
    - avg_rating is the true DB average across ALL lessons in the course.
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
 
    from .models import LessonRating, Lesson as _Lesson
    from django.db.models import Avg, Count
 
    lesson = get_object_or_404(_Lesson, id=lesson_id)
    course = lesson.section.course
 
    is_owner = has_full_course_access(request.user, course)
    if not is_owner and not _is_enrolled(request.user, course):
        return _json_error('Not enrolled.', 403)
 
    data = _parse_body(request)
    try:
        rating_val = int(data.get('rating') or 0)
    except (TypeError, ValueError):
        return _json_error('Invalid rating value.')
 
    if not (1 <= rating_val <= 5):
        return _json_error('Rating must be 1–5.')
 
    existing = LessonRating.objects.filter(lesson=lesson, user=request.user).first()
    updated = bool(existing)
 
    if existing:
        existing.rating = rating_val
        existing.save()
    else:
        LessonRating.objects.create(
            lesson=lesson,
            user=request.user,
            rating=rating_val,
        )
 
    # Aggregate: average across ALL lessons in this course
    agg = LessonRating.objects.filter(
        lesson__section__course=course
    ).aggregate(avg=Avg('rating'), total=Count('id'))
 
    avg = round(agg['avg'] or 0, 1)
    total = agg['total'] or 0
 
    return _json_ok({
        'your_rating': rating_val,
        'avg_rating': avg,
        'total_ratings': total,
        'already_rated': True,
        'updated': updated,
    })
 
 
@login_required
def lesson_rating_status(request, lesson_id):
    """
    GET /courses/lesson/<lesson_id>/rating-status/
    Returns the current user's rating + course average.
    """
    from .models import LessonRating, Lesson as _Lesson
    from django.db.models import Avg, Count
 
    lesson = get_object_or_404(_Lesson, id=lesson_id)
    course = lesson.section.course
 
    existing = LessonRating.objects.filter(lesson=lesson, user=request.user).first()
 
    agg = LessonRating.objects.filter(
        lesson__section__course=course
    ).aggregate(avg=Avg('rating'), total=Count('id'))
 
    return _json_ok({
        'your_rating': existing.rating if existing else None,
        'avg_rating': round(agg['avg'] or 0, 1),
        'total_ratings': agg['total'] or 0,
    })
 
 
# ─────────────────────────────────────────────────────────────────────────────
# LESSON ATTACHMENTS  (AJAX + Form POST)
# ─────────────────────────────────────────────────────────────────────────────
 
@login_required
def lesson_attachment_upload(request, lesson_id):
    """
    POST /courses/lesson/<lesson_id>/attachment/upload/
    multipart/form-data: file (optional), file_url (optional), description
    Returns: JSON { ok, attachment: { id, name, url, description, ... } }
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
 
    from .models import LessonAttachment, Lesson as _Lesson
    lesson = get_object_or_404(_Lesson, id=lesson_id)
    course = lesson.section.course
 
    is_owner = has_full_course_access(request.user, course)
    if not is_owner and not _is_enrolled(request.user, course):
        return _json_error('Not enrolled.', 403)
 
    uploaded_file = request.FILES.get('file')
    file_url = request.POST.get('file_url', '').strip()
    description = request.POST.get('description', '').strip()[:300]
 
    if not uploaded_file and not file_url:
        return _json_error('Please provide a file or a URL.')
 
    # Limit file size: 20 MB
    if uploaded_file and uploaded_file.size > 20 * 1024 * 1024:
        return _json_error('File size must not exceed 20 MB.')
 
    attachment = LessonAttachment(
        lesson=lesson,
        user=request.user,
        description=description,
        is_instructor_upload=is_owner,
        file_url=file_url or '',
    )
    if uploaded_file:
        attachment.file = uploaded_file
    attachment.save()
 
    file_display_url = attachment.file.url if attachment.file else attachment.file_url
 
    return _json_ok({
        'attachment': {
            'id': attachment.id,
            'name': attachment.get_display_name(),
            'url': file_display_url,
            'description': attachment.description,
            'is_instructor_upload': attachment.is_instructor_upload,
            'uploaded_at': attachment.uploaded_at.strftime('%b %d, %Y'),
            'uploader': request.user.get_full_name() or request.user.username,
        }
    })
 
 
@login_required
def lesson_attachment_delete(request, lesson_id, attachment_id):
    """
    POST /courses/lesson/<lesson_id>/attachment/<attachment_id>/delete/
    Only uploader, course owner, or superuser can delete.
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
 
    from .models import LessonAttachment
    attachment = get_object_or_404(LessonAttachment, id=attachment_id, lesson_id=lesson_id)
    course = attachment.lesson.section.course
 
    can_delete = (
        attachment.user == request.user
        or request.user.is_superuser
        or has_full_course_access(request.user, course)
    )
    if not can_delete:
        return _json_error('Permission denied.', 403)
 
    attachment.delete()
    return _json_ok({'deleted': attachment_id})
