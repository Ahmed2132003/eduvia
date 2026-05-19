"""
workshops/views.py
==================
تم إزالة جميع اعتماديات نظام الاشتراكات والخطط.
الوصول محمي الآن عبر can_access_workshops (كورس نشط آخر 60 يوم).
"""

import unicodedata

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from core.access import can_access_workshops, ACCESS_DENIED_MESSAGE

from .models import LiveRecording, LiveSession


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _slugify_title(title: str) -> str:
    normalized = unicodedata.normalize('NFKD', title or '').encode(
        'ascii', 'ignore'
    ).decode('ascii')
    return slugify(normalized) or 'no-title'


def _access_denied(request):
    """رد موحَّد عند رفض الوصول."""
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({"detail": ACCESS_DENIED_MESSAGE}, status=403)
    messages.error(request, ACCESS_DENIED_MESSAGE)
    return redirect('/')


def _is_instructor(user) -> bool:
    """يتحقق من أن المستخدم مدرب."""
    try:
        return user.courses_profile.role == 'instructor'
    except Exception:
        return getattr(user, 'role', None) == 'instructor'


# ---------------------------------------------------------------------------
# Live Session List
# ---------------------------------------------------------------------------

@login_required
def live_session_list(request):
    """قائمة الجلسات الحية - يتطلب كورسًا نشطًا."""
    if not can_access_workshops(request.user):
        return _access_denied(request)

    current_time = timezone.now()
    active_sessions = LiveSession.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_active=True,
    )
    upcoming_sessions = LiveSession.objects.filter(
        start_time__gt=current_time
    ).order_by('start_time')[:5]

    user_sessions = None
    if _is_instructor(request.user):
        user_sessions = LiveSession.objects.filter(instructor=request.user)

    return render(request, 'workshops/live_session_list.html', {
        'active_sessions': active_sessions,
        'upcoming_sessions': upcoming_sessions,
        'user_sessions': user_sessions,
        'current_time': current_time,
        'is_instructor': _is_instructor(request.user),
    })


# ---------------------------------------------------------------------------
# Watch Live
# ---------------------------------------------------------------------------

@login_required
def watch_live(request, session_id, slugified_title):
    """مشاهدة جلسة حية - يتطلب كورسًا نشطًا."""
    if not can_access_workshops(request.user):
        return _access_denied(request)

    session = get_object_or_404(LiveSession, id=session_id, is_active=True)

    session.participants.add(request.user)

    return render(request, 'workshops/watch_live.html', {
        'session': session,
        'slugified_title': _slugify_title(session.title),
    })


# ---------------------------------------------------------------------------
# Watch Recording
# ---------------------------------------------------------------------------

@login_required
def watch_recording(request, recording_id, slugified_title):
    """مشاهدة تسجيل جلسة - يتطلب كورسًا نشطًا."""
    if not can_access_workshops(request.user):
        return _access_denied(request)

    recording = get_object_or_404(LiveRecording, id=recording_id)

    return render(request, 'workshops/watch_recording.html', {
        'recording': recording,
        'slugified_title': _slugify_title(recording.live_session.title),
    })


# ---------------------------------------------------------------------------
# Create Live Session (Instructor only)
# ---------------------------------------------------------------------------

@login_required
def create_live_session(request):
    """إنشاء جلسة حية - للمدرسين الذين لديهم كورس نشط."""
    if not can_access_workshops(request.user):
        return _access_denied(request)

    if not _is_instructor(request.user):
        messages.error(request, 'إنشاء جلسات حية متاح للمدرسين فقط.')
        return redirect('workshops:live_session_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        meet_link = request.POST.get('meet_link', '').strip()
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        session_image = request.POST.get('session_image', '')

        if not all([title, meet_link, start_time, end_time]):
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة.')
            return render(request, 'workshops/create_live_session.html')

        session = LiveSession.objects.create(
            title=title,
            description=description,
            meet_link=meet_link,
            session_image=session_image,
            instructor=request.user,
            start_time=start_time,
            end_time=end_time,
            is_active=False,
        )
        messages.success(request, 'تم إنشاء الجلسة بنجاح!')
        return redirect(
            'workshops:start_live',
            session_id=session.id,
            slugified_title=_slugify_title(session.title),
        )

    return render(request, 'workshops/create_live_session.html')


# ---------------------------------------------------------------------------
# Start Live (Instructor only)
# ---------------------------------------------------------------------------

@login_required
def start_live(request, session_id, slugified_title):
    """بدء جلسة حية - للمدرس المالك فقط، يتطلب كورسًا نشطًا."""
    if not can_access_workshops(request.user):
        return _access_denied(request)

    if not _is_instructor(request.user):
        messages.error(request, 'بدء الجلسات متاح للمدرسين فقط.')
        return redirect('workshops:live_session_list')

    session = get_object_or_404(
        LiveSession, id=session_id, instructor=request.user, is_active=False
    )

    if request.method == 'POST':
        now = timezone.now()
        if session.start_time <= now <= session.end_time:
            session.is_active = True
            session.save()
            messages.success(request, 'تم بدء الجلسة بنجاح!')
            return redirect(session.meet_link)
        messages.error(request, 'الوقت الحالي خارج نطاق الجلسة المحددة.')

    return render(request, 'workshops/start_live.html', {
        'session': session,
        'slugified_title': _slugify_title(session.title),
    })


# ---------------------------------------------------------------------------
# Upload Recording (Instructor only)
# ---------------------------------------------------------------------------

@login_required
def upload_recording(request, session_id, slugified_title):
    """رفع تسجيل الجلسة - للمدرس المالك فقط، يتطلب كورسًا نشطًا."""
    if not can_access_workshops(request.user):
        return _access_denied(request)

    if not _is_instructor(request.user):
        messages.error(request, 'رفع التسجيلات متاح للمدرسين فقط.')
        return redirect('workshops:live_session_list')

    session = get_object_or_404(
        LiveSession, id=session_id, instructor=request.user
    )

    if request.method == 'POST':
        video_file = request.POST.get('video_file', '').strip()
        if video_file:
            if 'drive.google.com' in video_file and '/view' in video_file:
                video_file = (
                    video_file.replace('/view', '/preview')
                               .replace('?usp=sharing', '')
                )
            try:
                LiveRecording.objects.create(
                    live_session=session, video_file=video_file
                )
                messages.success(request, 'تم رفع التسجيل بنجاح!')
                return redirect('workshops:live_session_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ التسجيل: {e}')
        else:
            messages.error(request, 'يرجى تقديم رابط فيديو صالح.')

    return render(request, 'workshops/upload_recording.html', {
        'session': session,
        'slugified_title': _slugify_title(session.title),
    })