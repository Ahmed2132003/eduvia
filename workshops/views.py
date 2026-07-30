"""
workshops/views.py
==================
تم إزالة جميع اعتماديات نظام الاشتراكات والخطط.
الوصول محمي الآن عبر can_access_workshops (كورس نشط آخر 60 يوم) للجلسات
العادية (اللي مش تابعة لأي جروب).

Part 13 — نظام جروبات المناهج (Eduvia):
- الجلسات التابعة لجروب (LiveSession.group مش فاضي) بقت خاصة: مش بتظهر
  في القايمة العامة (active_sessions / upcoming_sessions) خالص، والوصول
  ليها (watch_live / watch_recording) بقى محكوم بعضوية الجروب
  (groups.GroupMembership) أو ملكية الجروب (المدرس صاحب الجروب) بدل
  can_access_workshops العادية — تفاصيل القرار في PROGRESS.md.
- الجلسات العادية (group=None) شغالة بالظبط زي ما كانت من غير أي تغيير.

Part 15 — تجميد الاشتراكات المنتهية تلقائيًا:
- watch_live وwatch_recording بقوا بيتأكدوا كمان (لغير صاحب الجروب) إن
  اشتراك الجروب لسه "نشط" فعليًا دلوقتي عن طريق
  groups.access.is_group_content_accessible، مش بس إن اليوزر عضو/صاحب
  فيه (اللي كان الفحص الوحيد من Part 13). لو الجروب متجمد (الاشتراك
  خلص)، الطالب بيترفض برسالة GROUP_FROZEN_MESSAGE بدل ما يدخل الجلسة.
  المدرس صاحب الجروب فضل يقدر يدخل حتى لو الجروب متجمد (يحتاج كمان
  can_access_workshops الأساسية زي أي مكان تاني، بس المقصود هنا إنه مش
  بيترفض بسبب تجميد اشتراك الجروب تحديدًا).

Part 17 — مكافآت XP للحضور:
- watch_live بقت بتمنح XP ثابتة (groups.constants.LIVE_SESSION_ATTENDANCE_XP)
  للطالب أول مرة يحضر فيها جلسة لايف تابعة لجروب، عن طريق دالة
  _grant_group_attendance_xp — تفاصيل القرار كاملة في PROGRESS.md.
  watch_recording متغيرتش خالص (مفيش XP لمشاهدة تسجيل، بس للحضور
  اللايف الفعلي).

Part 18 — معاينة مجانية تسويقية:
- view جديد free_previews_list: صفحة عامة (من غير تسجيل دخول — مفيش
  @login_required عليها عمدًا) بتعرض كل LiveRecording اتعلّم
  is_free_preview=True وتابع لجلسة تابعة لجروب. تفاصيل القرار كاملة في
  PROGRESS.md. باقي الـ views كلها (watch_live/watch_recording/إلخ)
  متلمستش خالص في الجزء ده.
"""

import unicodedata

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import Profile
from core.access import can_access_workshops, ACCESS_DENIED_MESSAGE
from groups.access import is_group_content_accessible, GROUP_FROZEN_MESSAGE
from groups.constants import LIVE_SESSION_ATTENDANCE_XP
from groups.models import GroupMembership

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


def _can_access_group_session(user, session) -> bool:
    """
    Part 13: فحص وصول لجلسة لايف تابعة لجروب (session.group مش None).

    بنفس روح core/decorators.py (دالة فحص بسيطة بترجع True/False، والـ
    view هو اللي بيقرر شكل الرد المناسب لو الفحص فشل) — مش استخدمنا
    require_course_access() نفسه لإنه مبني على فحص عام مالوش سياق
    (checker_fn(user) بس)، وهنا محتاجين نفحص بالنسبة لكائن (group) معين.

    مسموح لصاحب الجلسة دي وصول لو:
    - هو المدرس صاحب الجروب (group.teacher)، أو
    - هو طالب عضو فعلي في الجروب (groups.GroupMembership).
    """
    group = session.group
    if group is None:
        return True

    if group.teacher_id == user.id:
        return True

    return GroupMembership.objects.filter(student=user, group=group).exists()


def _group_access_denied(request):
    """رد موحَّد لما اليوزر يحاول يوصل لجلسة تابعة لجروب هو مش عضو/صاحب فيه."""
    message = 'الجلسة دي خاصة بأعضاء جروب معين، ومش عندك صلاحية توصلها.'
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({"detail": message}, status=403)
    messages.error(request, message)
    return redirect('workshops:live_session_list')


def _group_frozen_denied(request):
    """
    Part 15: رد موحَّد لما الجلسة تابعة لجروب عضويته سليمة (اليوزر عضو
    فعلي فيه) لكن اشتراك الجروب نفسه منتهي/متجمد دلوقتي.
    """
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({"detail": GROUP_FROZEN_MESSAGE}, status=403)
    messages.error(request, GROUP_FROZEN_MESSAGE)
    return redirect('workshops:live_session_list')


def _grant_group_attendance_xp(user, session):
    """
    Part 17: يمنح XP ثابتة (LIVE_SESSION_ATTENDANCE_XP) للطالب أول مرة
    يحضر فيها جلسة لايف تابعة لجروب (session.group مش None).

    شروط المنح:
    - الجلسة لازم تكون تابعة لجروب (group مش فاضي) — جلسات عادية
      (group=None) متضربش أي XP في الجزء ده، زي ما اتطلب بالظبط
      ("لما يحضر لايف سيشن جوه جروب").
    - المستخدم لازم يكون طالب، مش المدرس صاحب الجروب (المدرس مش "حاضر"
      بمعنى الكلمة، هو صاحب الجلسة).
    - أول حضور بس — بيتفحص عن طريق session.participants (ManyToMany
      موجود بالفعل على LiveSession، ومستخدم أصلاً في نفس الـ view قبل
      الجزء ده لتسجيل الحضور) قبل .add() مباشرة، عشان نمنع منح XP
      متكرر لو نفس الطالب فتح صفحة نفس الجلسة أكتر من مرة.
    """
    if session.group_id is None:
        return
    if session.group.teacher_id == user.id:
        return

    already_attended = session.participants.filter(id=user.id).exists()
    if already_attended:
        return

    profile, _ = Profile.objects.get_or_create(user=user)
    profile.xp += LIVE_SESSION_ATTENDANCE_XP
    profile.save(update_fields=['xp'])


# ---------------------------------------------------------------------------
# Live Session List
# ---------------------------------------------------------------------------

@login_required
def live_session_list(request):
    """
    قائمة الجلسات الحية - يتطلب كورسًا نشطًا.

    Part 13: القايمة العامة (active_sessions / upcoming_sessions) بقت
    مستبعدة منها أي جلسة تابعة لجروب (group__isnull=True) عشان الجلسات
    دي بقت تتعرض جوه صفحة الجروب نفسه (groups:group_detail) بدل الصفحة
    العامة دي — ده هو جوهر هدف الجزء ("الحصص اللايف بتبقى جوه الجروب بدل
    ما تكون عامة"). قسم "جلساتك" (user_sessions) الخاص بالمدرس فضل من
    غير فلترة عمدًا، عشان المدرس يقدر يدير كل جلساته (تابعة لجروب أو لأ)
    من مكان واحد ويقدر يعمل Start Live / Upload Recording عادي.
    """
    if not can_access_workshops(request.user):
        return _access_denied(request)

    current_time = timezone.now()
    active_sessions = LiveSession.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_active=True,
        group__isnull=True,
    )
    upcoming_sessions = LiveSession.objects.filter(
        start_time__gt=current_time,
        group__isnull=True,
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
# Free Previews (Public — Part 18)
# ---------------------------------------------------------------------------

def free_previews_list(request):
    """
    Part 18: صفحة عامة تسويقية — مفيش @login_required عليها عمدًا، عشان
    زوار المنصة (حتى لو مش مسجّلين دخول) يقدروا يشوفوا عينة من محتوى
    المدرسين قبل ما يقرروا ينضموا.

    بتعرض كل LiveRecording اتعلّم is_free_preview=True (عن طريق لوحة
    الأدمن، Part 18) وتابع لجلسة لايف مربوطة بجروب
    (live_session.group مش فاضي). تسجيلات مش تابعة لأي جروب مستبعدة
    من الصفحة دي حتى لو اتعلّمت is_free_preview بالغلط — الهدف
    التسويقي كله مبني على مسار "شوف عينة → انضم لجروب المدرس ده"
    (Part 11)، فمفيش معنى لعرض معاينة من غير جروب نودّي المستخدم له.

    كل عنصر في الصفحة بيعرض: عنوان الجلسة، اسم المدرس، فئة الجروب
    (دولة/مرحلة/صف)، رابط مشاهدة المعاينة (video_file)، وزرار واضح
    يودّي لصفحة انضمام المدرس (groups:join_teacher_community) عن طريق
    join_code بتاع الجروب نفسه.
    """
    previews = LiveRecording.objects.filter(
        is_free_preview=True,
        live_session__group__isnull=False,
    ).select_related(
        'live_session',
        'live_session__group',
        'live_session__group__teacher',
        'live_session__group__category',
    ).order_by('-uploaded_at')

    return render(request, 'workshops/free_previews_list.html', {
        'previews': previews,
    })


# ---------------------------------------------------------------------------
# Watch Live
# ---------------------------------------------------------------------------

@login_required
def watch_live(request, session_id, slugified_title):
    """
    مشاهدة جلسة حية.

    Part 13: لو الجلسة تابعة لجروب (session.group مش None)، الوصول بقى
    محكوم بعضوية/ملكية الجروب (_can_access_group_session) بدل
    can_access_workshops العادية — لإن دخول الجروب ده مسار دفع منفصل
    تمامًا عن اشتراك الكورسات العادي. لو الجلسة مش تابعة لأي جروب،
    السلوك القديم فاضل زي ما هو بالظبط.

    Part 17: بعد ما الوصول يتأكد ويتسمح، بنمنح XP ثابتة للطالب (مش
    المدرس) أول مرة يحضر فيها الجلسة دي (تفاصيل كاملة في
    _grant_group_attendance_xp). المنح بيحصل قبل .participants.add()
    مباشرة عشان الفحص (already_attended) يبقى دقيق.
    """
    session = get_object_or_404(LiveSession, id=session_id, is_active=True)

    if session.group_id:
        if not _can_access_group_session(request.user, session):
            return _group_access_denied(request)
        # Part 15: عضويته سليمة، لكن لازم كمان اشتراك الجروب يبقى نشط
        # فعليًا دلوقتي — المدرس صاحب الجروب مستثنى من الفحص ده (يقدر
        # يدخل حتى لو الجروب متجمد، عشان يقدر يدير ويجدد).
        if session.group.teacher_id != request.user.id:
            if not is_group_content_accessible(session.group):
                return _group_frozen_denied(request)
    else:
        if not can_access_workshops(request.user):
            return _access_denied(request)

    # Part 17: منح XP الحضور — لازم يحصل قبل .add() عشان فحص "أول حضور"
    # يبقى دقيق (تفاصيل كاملة جوه الدالة نفسها).
    _grant_group_attendance_xp(request.user, session)

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
    """
    مشاهدة تسجيل جلسة.

    Part 13: نفس منطق watch_live بالظبط — لو التسجيل تابع لجلسة تابعة
    لجروب، الوصول محكوم بعضوية/ملكية الجروب بدل can_access_workshops.

    Part 17: مفيش أي منح XP هنا عمدًا — المكافأة مقصورة على "الحضور"
    الفعلي للايف (watch_live)، مش مشاهدة التسجيل بعدين.

    Part 18: ملحوظة — الوصول هنا (لو التسجيل تابع لجروب) لسه محكوم
    بعضوية/ملكية الجروب + اشتراك نشط، حتى لو نفس التسجيل ده معروض في
    صفحة free_previews_list العامة. الصفحتين مستقلتين تمامًا: الصفحة
    العامة بتعرض بس رابط video_file مباشرة للزوار (من غير أي فحص وصول)،
    ومفيش أي تعديل هنا على watch_recording نفسها.
    """
    recording = get_object_or_404(
        LiveRecording.objects.select_related('live_session'), id=recording_id
    )

    if recording.live_session.group_id:
        if not _can_access_group_session(request.user, recording.live_session):
            return _group_access_denied(request)
        # Part 15: نفس منطق watch_live بالظبط.
        if recording.live_session.group.teacher_id != request.user.id:
            if not is_group_content_accessible(recording.live_session.group):
                return _group_frozen_denied(request)
    else:
        if not can_access_workshops(request.user):
            return _access_denied(request)

    return render(request, 'workshops/watch_recording.html', {
        'recording': recording,
        'slugified_title': _slugify_title(recording.live_session.title),
    })


# ---------------------------------------------------------------------------
# Create Live Session (Instructor only)
# ---------------------------------------------------------------------------

@login_required
def create_live_session(request):
    """
    إنشاء جلسة حية - للمدرسين الذين لديهم كورس نشط.

    ملحوظة Part 13: الفورم/التمبلت (create_live_session.html) متعدلش في
    الجزء ده لإن ملفه مكانش متاح، فمفيش اختيار مباشر لجروب وقت الإنشاء.
    الجلسة بتتعمل عادي (group=None)، وبعدين المدرس يقدر يربطها بأي جروب
    بتاعه من صفحة الجروب نفسها (groups:group_detail → "ضيف جلسة موجودة
    لهذا الجروب") — تفاصيل القرار موثقة في PROGRESS.md.
    """
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