"""
courses/views_curriculum.py  (v2 — with LessonTask system + Certificate)
────────────────────────────────────────────────────────────────────────────────
Instructor views:
  curriculum_builder, section_create/update/delete/reorder,
  lesson_create/update/delete/reorder,
  lesson_task_create/update/delete   ← NEW

Student views:
  course_curriculum_view, lesson_view, lesson_progress_update,
  lesson_comment_add/delete, lesson_rate, lesson_rating_status,
  lesson_attachment_upload/delete,
  lesson_task_submit                 ← NEW
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Avg, Count

from core.ownership import is_course_owner, has_full_course_access
from .decorators import instructor_required
from .models import (
    Course, CourseEnrollment, Lesson, LessonProgress,
    Section, UserProfile, VideoProgress,
    LessonTask, LessonTaskSubmission,
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
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if has_full_course_access(user, course):
        return True
    if CourseEnrollment.objects.filter(user=user, course=course).exists():
        return True
    try:
        from marketplace.models import Enrollment as ME
        if ME.objects.filter(student=user, course=course, is_active=True).exists():
            return True
    except Exception:
        pass
    return False

def _parse_body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return dict(request.POST)

def _section_data(section):
    return {
        'id': section.id, 'title': section.title, 'order': section.order,
        'lessons': [_lesson_data(l) for l in section.lessons.order_by('order')],
    }

def _lesson_data(lesson):
    return {
        'id': lesson.id, 'title': lesson.title,
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

def _task_data(task):
    return {
        'id': task.id,
        'task_type': task.task_type,
        'title': task.title,
        'description': task.description,
        'questions': task.questions,
        'passing_score': task.passing_score,
        'external_url': task.external_url,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CURRICULUM BUILDER
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def curriculum_builder(request, course_id, course_slug):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_superuser and not is_course_owner(request.user, course):
        messages.error(request, "غير مصرح لك بتعديل منهج هذا الكورس.")
        return redirect('courses:instructor_dashboard')

    sections = course.sections.prefetch_related('lessons').order_by('order')
    course_slug_clean = slugify(clean_text(course.title), allow_unicode=True) or 'default'

    return render(request, 'courses/curriculum_builder.html', {
        'course': course,
        'sections': sections,
        'course_slug': course_slug_clean,
    })


# ─────────────────────────────────────────────────────────────────────────────
# SECTION CRUD
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def section_create(request, course_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    data = _parse_body(request)
    title = str(data.get('title') or '').strip()
    if not title:
        return _json_error('Section title is required.')
    section = Section.objects.create(
        course=course, title=title,
        order=Section.objects.filter(course=course).count(),
    )
    return _json_ok({'section': _section_data(section)})


@login_required
@instructor_required
def section_update(request, course_id, section_id):
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
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    section.delete()
    for idx, s in enumerate(Section.objects.filter(course=course).order_by('order')):
        if s.order != idx:
            s.order = idx
            s.save(update_fields=['order'])
    return _json_ok({'deleted': section_id})


@login_required
@instructor_required
def section_reorder(request, course_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    data = _parse_body(request)
    ordered_ids = data.get('order', [])
    if not isinstance(ordered_ids, list):
        return _json_error('Invalid payload.')
    for idx, sid in enumerate(ordered_ids):
        try:
            Section.objects.filter(id=int(sid), course=course).update(order=idx)
        except (ValueError, TypeError):
            pass
    return _json_ok()


# ─────────────────────────────────────────────────────────────────────────────
# LESSON CRUD
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def lesson_create(request, course_id, section_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    from .models import Video
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    data = _parse_body(request)

    existing_video_id = data.get('existing_video_id')
    legacy_video = None
    if existing_video_id:
        try:
            legacy_video = Video.objects.get(id=int(existing_video_id), course=course)
        except (Video.DoesNotExist, ValueError, TypeError):
            return _json_error('الفيديو المحدد غير موجود.')

    title       = str(data.get('title') or (legacy_video.title if legacy_video else '')).strip()
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

    is_preview  = bool(data.get('is_preview', False))
    description = str(data.get('description') or (legacy_video.description if legacy_video else '')).strip()
    content     = str(data.get('content') or '').strip()

    if not title:
        return _json_error('Lesson title is required.')
    if lesson_type == 'video' and not video_url:
        return _json_error('Video URL is required for video lessons.')
    if lesson_type != 'video' and not content:
        return _json_error('Content is required for text/article lessons.')

    lesson = Lesson.objects.create(
        section=section, title=title, lesson_type=lesson_type,
        order=section.lessons.count(),
        video_url=video_url if lesson_type == 'video' else None,
        video_duration=video_duration, is_preview=is_preview,
        description=description, content=content,
    )
    return _json_ok({'lesson': _lesson_data(lesson)})


@login_required
@instructor_required
def lesson_update(request, course_id, section_id, lesson_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course  = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    lesson  = get_object_or_404(Lesson, id=lesson_id, section=section)
    data    = _parse_body(request)

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

    lesson.title = title; lesson.lesson_type = lesson_type
    lesson.video_url = video_url if lesson_type == 'video' else None
    lesson.video_duration = video_duration; lesson.is_preview = is_preview
    lesson.description = description; lesson.content = content
    lesson.save()
    return _json_ok({'lesson': _lesson_data(lesson)})


@login_required
@instructor_required
def lesson_delete(request, course_id, section_id, lesson_id):
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
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course  = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    data = _parse_body(request)
    ordered_ids = data.get('order', [])
    if not isinstance(ordered_ids, list):
        return _json_error('Invalid payload.')
    for idx, lid in enumerate(ordered_ids):
        try:
            Lesson.objects.filter(id=int(lid), section=section).update(order=idx)
        except (ValueError, TypeError):
            pass
    return _json_ok()


# ─────────────────────────────────────────────────────────────────────────────
# LESSON TASK CRUD  (Instructor — AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@instructor_required
def lesson_task_create(request, course_id, section_id, lesson_id):
    """
    POST /courses/instructor/curriculum/<cid>/section/<sid>/lesson/<lid>/task/create/
    Body: {
      task_type, title, description, questions, passing_score, external_url
    }
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    lesson  = get_object_or_404(Lesson, id=lesson_id, section=section)

    # Only one task per lesson
    if hasattr(lesson, 'task'):
        return _json_error('This lesson already has a task. Use update instead.')

    data = _parse_body(request)
    task_type    = str(data.get('task_type') or 'mcq')
    title        = str(data.get('title') or '').strip()
    description  = str(data.get('description') or '').strip()
    questions    = data.get('questions', [])
    external_url = str(data.get('external_url') or '').strip()
    try:
        passing_score = int(data.get('passing_score') or 70)
        passing_score = max(0, min(100, passing_score))
    except (ValueError, TypeError):
        passing_score = 70

    if not title:
        return _json_error('Task title is required.')
    if task_type == 'mcq' and not questions:
        return _json_error('MCQ tasks require at least one question.')
    if task_type == 'external_link' and not external_url:
        return _json_error('External link tasks require a URL.')

    task = LessonTask.objects.create(
        lesson=lesson, task_type=task_type, title=title,
        description=description, questions=questions if isinstance(questions, list) else [],
        passing_score=passing_score, external_url=external_url,
        order=0,
    )
    return _json_ok({'task': _task_data(task)})


@login_required
@instructor_required
def lesson_task_update(request, course_id, section_id, lesson_id):
    """
    POST /courses/instructor/curriculum/<cid>/section/<sid>/lesson/<lid>/task/update/
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    lesson  = get_object_or_404(Lesson, id=lesson_id, section=section)
    task    = get_object_or_404(LessonTask, lesson=lesson)
    data    = _parse_body(request)

    task.task_type    = str(data.get('task_type') or task.task_type)
    task.title        = str(data.get('title') or task.title).strip()
    task.description  = str(data.get('description') or '').strip()
    task.external_url = str(data.get('external_url') or '').strip()
    questions = data.get('questions')
    if questions is not None:
        task.questions = questions if isinstance(questions, list) else []
    try:
        ps = int(data.get('passing_score') or task.passing_score)
        task.passing_score = max(0, min(100, ps))
    except (ValueError, TypeError):
        pass
    task.save()
    return _json_ok({'task': _task_data(task)})


@login_required
@instructor_required
def lesson_task_delete(request, course_id, section_id, lesson_id):
    """
    POST /courses/instructor/curriculum/<cid>/section/<sid>/lesson/<lid>/task/delete/
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    course = get_object_or_404(Course, id=course_id)
    if not is_course_owner(request.user, course):
        return _json_error('Unauthorized', 403)
    section = get_object_or_404(Section, id=section_id, course=course)
    lesson  = get_object_or_404(Lesson, id=lesson_id, section=section)
    task    = get_object_or_404(LessonTask, lesson=lesson)
    task.delete()
    return _json_ok({'deleted': True})


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT — COURSE CURRICULUM PAGE
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def course_curriculum_view(request, course_id, course_slug):
    course = get_object_or_404(Course, id=course_id)
    slugified = slugify(clean_text(course.title), allow_unicode=True) or 'default'
    if slugified != course_slug:
        return HttpResponsePermanentRedirect(
            reverse('courses:course_curriculum',
                    kwargs={'course_id': course_id, 'course_slug': slugified})
        )

    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)
    if not enrolled:
        messages.error(request, 'يجب شراء هذه الدورة لعرض المنهج.')
        return redirect('courses:courses')

    sections = course.sections.prefetch_related('lessons').order_by('order')
    completed_lesson_ids = set(
        LessonProgress.objects.filter(
            user=request.user, lesson__section__course=course, completed=True,
        ).values_list('lesson_id', flat=True)
    )

    total_lessons = completed_count = 0
    sections_data = []
    for section in sections:
        lessons = list(section.lessons.order_by('order'))
        sec_done = 0
        for lesson in lessons:
            lesson.is_completed = lesson.id in completed_lesson_ids
            if lesson.is_completed:
                sec_done += 1
        total_lessons   += len(lessons)
        completed_count += sec_done
        sections_data.append({'section': section, 'lessons': lessons,
                               'completed': sec_done, 'total': len(lessons)})

    progress_pct = round((completed_count / total_lessons * 100) if total_lessons else 0)

    return render(request, 'courses/course_curriculum.html', {
        'course': course, 'sections_data': sections_data,
        'total_lessons': total_lessons, 'completed_count': completed_count,
        'progress_pct': progress_pct, 'is_owner': is_owner,
        'is_enrolled': enrolled, 'course_slug': slugified,
    })


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT — LESSON VIEW
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_view(request, course_id, course_slug, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    slugified = slugify(clean_text(course.title), allow_unicode=True) or 'default'
    if slugified != course_slug:
        return HttpResponsePermanentRedirect(
            reverse('courses:lesson_view',
                    kwargs={'course_id': course_id, 'course_slug': slugified,
                            'lesson_id': lesson_id})
        )

    lesson   = get_object_or_404(Lesson, id=lesson_id, section__course=course)
    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)

    if not enrolled and not lesson.is_preview:
        messages.error(request, 'يجب شراء هذه الدورة لمشاهدة هذا الدرس.')
        return redirect('courses:courses')

    # ── Lesson Progress ───────────────────────────────────────────────────────
    lesson_progress, _ = LessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson,
        defaults={'completed': False, 'progress_percentage': 0.0},
    )
    # Text / Article: auto-complete on first view
    if lesson.lesson_type in ('text', 'article') and not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.progress_percentage = 100.0
        lesson_progress.save()

    # ── Task data ─────────────────────────────────────────────────────────────
    task = None
    task_passed = False
    best_submission = None
    try:
        task = lesson.task  # OneToOneField reverse
        best_submission = (
            LessonTaskSubmission.objects
            .filter(user=request.user, task=task, passed=True)
            .order_by('-score').first()
        )
        task_passed = best_submission is not None
    except LessonTask.DoesNotExist:
        pass

    # ── Sidebar ───────────────────────────────────────────────────────────────
    sections = course.sections.prefetch_related('lessons').order_by('order')
    completed_ids = set(
        LessonProgress.objects.filter(
            user=request.user, lesson__section__course=course, completed=True,
        ).values_list('lesson_id', flat=True)
    )

    # Pre-fetch which lessons have tasks + which ones the student passed
    passed_task_lesson_ids = set(
        LessonTaskSubmission.objects
        .filter(user=request.user, passed=True,
                task__lesson__section__course=course)
        .values_list('task__lesson_id', flat=True)
    )
    lessons_with_tasks = set(
        LessonTask.objects.filter(lesson__section__course=course)
        .values_list('lesson_id', flat=True)
    )

    sidebar_sections = []
    for section in sections:
        lessons_qs = list(section.lessons.order_by('order'))
        for l in lessons_qs:
            l.is_completed = l.id in completed_ids
            l.is_active    = l.id == lesson.id
            l.has_task     = l.id in lessons_with_tasks
            l.task_passed  = l.id in passed_task_lesson_ids
        sidebar_sections.append({'section': section, 'lessons': lessons_qs})

    # ── Prev / Next ────────────────────────────────────────────────────────────
    all_lessons = [l for s in sections for l in s.lessons.order_by('order')]
    lesson_ids  = [l.id for l in all_lessons]
    try:
        current_idx = lesson_ids.index(lesson.id)
    except ValueError:
        current_idx = -1
    prev_lesson = all_lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if 0 <= current_idx < len(all_lessons) - 1 else None

    # ── Certificate eligibility ───────────────────────────────────────────────
    total_lessons           = len(all_lessons)
    completed_lessons_count = len(completed_ids)
    all_lessons_done        = (total_lessons > 0 and completed_lessons_count >= total_lessons)
    show_certificate        = course.is_finished and all_lessons_done
    # Show preview card (conditions not all met) when enrolled student
    show_certificate_preview = enrolled and not is_owner and not show_certificate

    # ── Comments / Attachments ────────────────────────────────────────────────
    from .models import LessonComment, LessonAttachment
    comments    = LessonComment.objects.filter(lesson=lesson).select_related('user')[:50]
    attachments = LessonAttachment.objects.filter(lesson=lesson).select_related('user')

    return render(request, 'courses/lesson_view.html', {
        'course':           course,
        'lesson':           lesson,
        'lesson_progress':  lesson_progress,
        'sidebar_sections': sidebar_sections,
        'completed_ids':    completed_ids,
        'prev_lesson':      prev_lesson,
        'next_lesson':      next_lesson,
        'is_owner':         is_owner,
        'is_enrolled':      enrolled,
        'course_slug':      slugified,
        # task
        'task':             task,
        'task_passed':      task_passed,
        'best_submission':  best_submission,
        # certificate
        'show_certificate':         show_certificate,
        'show_certificate_preview': show_certificate_preview,
        'all_lessons_done':         all_lessons_done,
        'total_lessons':            total_lessons,
        'completed_lessons_count':  completed_lessons_count,
        # comments / attachments
        'comments':    comments,
        'attachments': attachments,
    })


# ─────────────────────────────────────────────────────────────────────────────
# LESSON PROGRESS  (AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_progress_update(request, lesson_id):
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

    duration_secs = (lesson.video_duration or 0) * 60
    if duration_secs > 0:
        current_time = min(current_time, duration_secs)
        raw_pct = (current_time / duration_secs) * 100
    else:
        raw_pct = 0

    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson,
    )

    # Anti-cheat: never allow backwards progress
    if raw_pct < lesson_progress.progress_percentage and not created:
        return _json_ok({
            'progress': round(lesson_progress.progress_percentage, 1),
            'completed': lesson_progress.completed,
            'threshold_reached': lesson_progress.progress_percentage >= 85,
        })

    lesson_progress.current_time        = current_time
    lesson_progress.progress_percentage = raw_pct
    threshold_reached = raw_pct >= 85

    newly_completed = False
    # Auto-complete at 90% — but ONLY if no task, or task already passed
    has_task = hasattr(lesson, 'task')
    task_ok  = False
    if has_task:
        try:
            task_ok = LessonTaskSubmission.objects.filter(
                user=request.user, task=lesson.task, passed=True
            ).exists()
        except Exception:
            task_ok = False

    can_complete = (not has_task) or task_ok
    if raw_pct >= 90 and not lesson_progress.completed and can_complete:
        lesson_progress.completed = True
        newly_completed = True
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


# ─────────────────────────────────────────────────────────────────────────────
# LESSON TASK SUBMIT  (Student — AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_task_submit(request, lesson_id):
    """
    POST /courses/lesson/<lesson_id>/task/submit/
    Handles all task types: mcq | essay | file_upload | external_link
    Returns: { ok, passed, score, feedback, correct_answers (MCQ only) }
    """
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)

    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course

    is_owner = has_full_course_access(request.user, course)
    enrolled = is_owner or _is_enrolled(request.user, course)
    if not enrolled:
        return _json_error('Not enrolled.', 403)

    # Get task
    try:
        task = lesson.task
    except LessonTask.DoesNotExist:
        return _json_error('This lesson has no task.', 404)

    # Determine next attempt number
    last_attempt = (
        LessonTaskSubmission.objects
        .filter(user=request.user, task=task)
        .order_by('-attempt_number')
        .values_list('attempt_number', flat=True)
        .first()
    ) or 0
    attempt_number = last_attempt + 1

    # ── Parse submission by type ──────────────────────────────────────────────
    task_type = task.task_type
    score     = 0.0
    passed    = False
    feedback  = ''
    submitted_answers    = []
    essay_answer         = ''
    file_url_val         = ''
    external_url_visited = False
    correct_answers      = []   # for MCQ client-side highlight

    if task_type == 'mcq':
        # JSON body
        try:
            body = json.loads(request.body)
        except Exception:
            body = {}
        submitted_answers = body.get('answers', [])
        questions = task.questions

        if len(submitted_answers) != len(questions):
            return _json_error('Answer count does not match question count.')

        correct_count = 0
        for ans, q in zip(submitted_answers, questions):
            ca = q.get('correct_answer', '')
            correct_answers.append(ca)
            if str(ans).strip() == str(ca).strip():
                correct_count += 1

        score  = (correct_count / len(questions)) * 100 if questions else 0
        passed = score >= task.passing_score
        feedback = (
            f'You got {correct_count}/{len(questions)} correct ({score:.0f}%).'
        )

    elif task_type == 'essay':
        try:
            body = json.loads(request.body)
        except Exception:
            body = {}
        essay_texts = body.get('essay_texts', [])
        essay_answer = '\n\n---\n\n'.join(essay_texts)
        if not essay_answer.strip():
            return _json_error('Essay answer cannot be empty.')
        # Essays are always "passed" upon submission (manual grading not implemented)
        score    = 100.0
        passed   = True
        feedback = 'Essay submitted successfully. Your instructor will review it.'

    elif task_type == 'file_upload':
        uploaded_file = request.FILES.get('file')
        file_url_val  = request.POST.get('file_url', '').strip()

        if not uploaded_file and not file_url_val:
            return _json_error('Please upload a file or enter a URL.')

        # Save file if uploaded
        if uploaded_file:
            from .models import LessonAttachment
            att = LessonAttachment.objects.create(
                lesson=lesson, user=request.user,
                file=uploaded_file,
                description='Task submission',
                is_instructor_upload=False,
            )
            file_url_val = att.file.url if att.file else file_url_val

        score    = 100.0
        passed   = True
        feedback = 'File submitted successfully.'

    elif task_type == 'external_link':
        try:
            body = json.loads(request.body)
        except Exception:
            body = {}
        visited = bool(body.get('external_url_visited', False))
        if not visited:
            return _json_error('Please confirm you visited the link.')
        external_url_visited = True
        score    = 100.0
        passed   = True
        feedback = 'External link activity confirmed.'

    else:
        return _json_error(f'Unknown task type: {task_type}')

    # ── Save submission ───────────────────────────────────────────────────────
    submission = LessonTaskSubmission.objects.create(
        task=task,
        user=request.user,
        attempt_number=attempt_number,
        submitted_answers=submitted_answers,
        essay_answer=essay_answer,
        file_url=file_url_val,
        external_url_visited=external_url_visited,
        score=score,
        passed=passed,
    )

    # ── If passed → auto-complete the lesson ─────────────────────────────────
    if passed:
        lp, _ = LessonProgress.objects.get_or_create(
            user=request.user, lesson=lesson,
        )
        if not lp.completed:
            lp.completed            = True
            lp.progress_percentage  = 100.0
            lp.save()
            # Award coins
            try:
                request.user.courses_profile.add_coins(50)
            except Exception:
                pass

    response_data = {
        'score':    round(score, 1),
        'passed':   passed,
        'feedback': feedback,
        'attempt':  attempt_number,
    }
    if task_type == 'mcq':
        response_data['correct_answers'] = correct_answers

    return _json_ok(response_data)


# ─────────────────────────────────────────────────────────────────────────────
# COMMENTS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_comment_add(request, lesson_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    from .models import LessonComment
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not _is_enrolled(request.user, lesson.section.course) and \
       not has_full_course_access(request.user, lesson.section.course):
        return _json_error('Not enrolled.', 403)
    data = _parse_body(request)
    content = str(data.get('content') or '').strip()
    if not content:
        return _json_error('Comment content is required.')
    if len(content) > 2000:
        return _json_error('Comment too long (max 2000 chars).')
    comment = LessonComment.objects.create(lesson=lesson, user=request.user, content=content)
    return _json_ok({'comment': {
        'id': comment.id,
        'user': request.user.get_full_name() or request.user.username,
        'username': request.user.username,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%b %d, %Y'),
    }})


@login_required
def lesson_comment_delete(request, lesson_id, comment_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    from .models import LessonComment
    comment = get_object_or_404(LessonComment, id=comment_id, lesson_id=lesson_id)
    if comment.user != request.user and not request.user.is_superuser:
        return _json_error('Permission denied.', 403)
    comment.delete()
    return _json_ok({'deleted': comment_id})


# ─────────────────────────────────────────────────────────────────────────────
# RATINGS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_rate(request, lesson_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    from .models import LessonRating
    lesson = get_object_or_404(Lesson, id=lesson_id)
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
    updated  = bool(existing)
    if existing:
        existing.rating = rating_val; existing.save()
    else:
        LessonRating.objects.create(lesson=lesson, user=request.user, rating=rating_val)
    agg = LessonRating.objects.filter(
        lesson__section__course=course
    ).aggregate(avg=Avg('rating'), total=Count('id'))
    avg   = round(agg['avg'] or 0, 1)
    total = agg['total'] or 0
    return _json_ok({'your_rating': rating_val, 'avg_rating': avg,
                     'total_ratings': total, 'already_rated': True, 'updated': updated})


@login_required
def lesson_rating_status(request, lesson_id):
    from .models import LessonRating
    lesson   = get_object_or_404(Lesson, id=lesson_id)
    existing = LessonRating.objects.filter(lesson=lesson, user=request.user).first()
    agg = LessonRating.objects.filter(
        lesson__section__course=lesson.section.course
    ).aggregate(avg=Avg('rating'), total=Count('id'))
    return _json_ok({
        'your_rating':   existing.rating if existing else None,
        'avg_rating':    round(agg['avg'] or 0, 1),
        'total_ratings': agg['total'] or 0,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ATTACHMENTS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def lesson_attachment_upload(request, lesson_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    from .models import LessonAttachment
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course
    is_owner = has_full_course_access(request.user, course)
    if not is_owner and not _is_enrolled(request.user, course):
        return _json_error('Not enrolled.', 403)
    uploaded_file = request.FILES.get('file')
    file_url      = request.POST.get('file_url', '').strip()
    description   = request.POST.get('description', '').strip()[:300]
    if not uploaded_file and not file_url:
        return _json_error('Please provide a file or a URL.')
    if uploaded_file and uploaded_file.size > 20 * 1024 * 1024:
        return _json_error('File size must not exceed 20 MB.')
    att = LessonAttachment(
        lesson=lesson, user=request.user, description=description,
        is_instructor_upload=is_owner, file_url=file_url or '',
    )
    if uploaded_file:
        att.file = uploaded_file
    att.save()
    file_display_url = att.file.url if att.file else att.file_url
    return _json_ok({'attachment': {
        'id': att.id, 'name': att.get_display_name(), 'url': file_display_url,
        'description': att.description, 'is_instructor_upload': att.is_instructor_upload,
        'uploaded_at': att.uploaded_at.strftime('%b %d, %Y'),
        'uploader': request.user.get_full_name() or request.user.username,
    }})


@login_required
def lesson_attachment_delete(request, lesson_id, attachment_id):
    if request.method != 'POST':
        return _json_error('Method not allowed.', 405)
    from .models import LessonAttachment
    att    = get_object_or_404(LessonAttachment, id=attachment_id, lesson_id=lesson_id)
    course = att.lesson.section.course
    can_delete = (
        att.user == request.user or request.user.is_superuser
        or has_full_course_access(request.user, course)
    )
    if not can_delete:
        return _json_error('Permission denied.', 403)
    att.delete()
    return _json_ok({'deleted': attachment_id})