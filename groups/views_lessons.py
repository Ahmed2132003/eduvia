"""
groups/views_lessons.py
========================
Part 28 (المرحلة الثانية) — واجهات رفع/عرض الدروس المسجلة (موديل
GroupLesson من Part 27) داخل الجروب.

قرار تنظيمي (مش قرار معماري وظيفي): الـ views دي في ملف منفصل عن
groups/views.py بدل ما تتضاف جواه زي باقي الأجزاء اللي فاتت. groups/views.py
بقى فيه أكتر من 1300 سطر، وضيف views جديدة عليه هيخليه أكبر وأصعب في
المراجعة/التعديل لاحقًا (وهيستهلك تحقيق أكبر بكتير من الـ context في أي
جلسة تانية تحتاج تعدّل فيه). بدل كده، بدأنا نقسّم views الجروبات على ملفات
حسب الموضوع (lessons هنا) — القرار ده تنظيمي بحت، مفيش أي تغيير في
السلوك أو أسماء الـ URLs بسببه. لو Ahmed حابب نفس الأسلوب في الأجزاء
الجاية (الواجبات Part 34، المهام اليومية Part 35، إلخ)، سهل نكمل نفس
النمط (views_assignments.py، views_todos.py، ...).

الـ helpers المشتركة (instructor_required، _get_owned_group_or_403،
_get_group_and_membership_or_403) اتستوردت من groups/views.py بدل ما
تتكرر هنا — نفس الفلسفة المتبعة في كل الأجزاء اللي فاتت (مصدر حقيقة واحد
لكل فحص صلاحية).

نفس أسلوب الكود المتبع في باقي groups/views.py: function-based views +
render + templates (مفيش class-based views، ومفيش Django Form/ModelForm
جديد — نفس أسلوب create_live_session (Part 24) في قراءة request.POST
يدويًا لثلاث/أربع حقول بسيطة).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .access import is_group_content_accessible, GROUP_FROZEN_MESSAGE
from .models import GroupLesson, TeacherGroup
from .views import (
    instructor_required,
    _get_owned_group_or_403,
    _get_group_and_membership_or_403,
)


# ---------------------------------------------------------------------------
# Part 28: رفع درس مسجل جديد (المدرس صاحب الجروب بس)
# ---------------------------------------------------------------------------

@instructor_required
def upload_group_lesson(request, group_id):
    """
    GET: يعرض فورم رفع درس جديد (عنوان، وصف، رابط فيديو، مدة الفيديو،
         ترتيب)، بالإضافة لاختيار 'انشر دلوقتي' أو 'جدولة لوقت لاحق' —
         نفس نمط start_choice المستخدم في create_live_session (Part 24)
         بالظبط، عشان يبقى فيه طريقة فعلية تنتج بيها دروس
         is_published=False + publish_at محدد (اللي Part 31 هيدور عليها
         لاحقًا وينشرها تلقائيًا بالـ Celery task). الحقلين (is_published،
         publish_at) كانوا موجودين على الموديل من Part 27 بس من غير أي
         واجهة تملاهم — دلوقتي بقى فيه طريقة فعلية.
    POST: بيتحقق من الحقول الأساسية (عنوان + رابط فيديو إجباريين)،
         ولو 'جدولة' لازم كمان publish_at. بينشئ GroupLesson مربوطة
         بالجروب، ويرجّع المدرس لقايمة دروس الجروب.
    """
    group = _get_owned_group_or_403(request, group_id)

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        description = (request.POST.get('description') or '').strip()
        video_url = (request.POST.get('video_url') or '').strip()
        video_duration_raw = (request.POST.get('video_duration') or '').strip()
        order_raw = (request.POST.get('order') or '').strip()
        publish_choice = request.POST.get('publish_choice')  # 'now' | 'schedule'

        errors = []
        if not title:
            errors.append('من فضلك اكتب عنوان الدرس.')
        if not video_url:
            errors.append('من فضلك حط رابط الفيديو.')

        video_duration = 0
        if video_duration_raw:
            try:
                video_duration = float(video_duration_raw)
            except ValueError:
                errors.append('مدة الفيديو لازم تكون رقم.')

        order = 0
        if order_raw:
            try:
                order = int(order_raw)
            except ValueError:
                errors.append('الترتيب لازم يكون رقم صحيح.')

        publish_at = None
        is_published = True
        if publish_choice == 'schedule':
            is_published = False
            publish_at_raw = request.POST.get('publish_at')
            if not publish_at_raw:
                errors.append('من فضلك حدد ميعاد النشر المجدول.')
            else:
                try:
                    parsed_publish_at = timezone.datetime.fromisoformat(publish_at_raw)
                except ValueError:
                    errors.append('صيغة ميعاد النشر مش صحيحة.')
                else:
                    if timezone.is_naive(parsed_publish_at):
                        parsed_publish_at = timezone.make_aware(parsed_publish_at)
                    publish_at = parsed_publish_at
        elif publish_choice != 'now':
            errors.append('من فضلك اختار هتنشر الدرس دلوقتي ولا هتجدوله.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'groups/upload_group_lesson.html', {
                'group': group,
                'form_data': request.POST,
            })

        GroupLesson.objects.create(
            group=group,
            title=title,
            description=description,
            video_url=video_url,
            video_duration=video_duration,
            order=order,
            is_published=is_published,
            publish_at=publish_at,
        )
        messages.success(request, 'تم رفع الدرس بنجاح.')
        return redirect('groups:group_lessons_list', group_id=group.id)

    return render(request, 'groups/upload_group_lesson.html', {
        'group': group,
        'form_data': None,
    })


# ---------------------------------------------------------------------------
# Part 28: قايمة دروس الجروب (المدرس صاحب الجروب + الطالب العضو)
# ---------------------------------------------------------------------------

@login_required
def group_lessons_list(request, group_id):
    """
    نفس فحص الصلاحية المستخدم في group_recordings/watch_group_recording
    (Part 26) بالظبط — عضوية فعلية أو ownership، وبعدين (للطالب العضو بس،
    مش المدرس) لازم الجروب يكون "نشط" (is_group_content_accessible)
    وإلا بيترجع لصفحة "جروباتي" برسالة التجميد المعتادة.

    المدرس صاحب الجروب: بيشوف كل الدروس (منشورة وغير منشورة/مجدولة)
    مرتبة بالـ order، مع علامة واضحة لكل درس غير منشور لو ليه publish_at
    محدد ("هتنزل يوم كذا") زي ما اتطلب بالظبط في نص الجزء.
    الطالب العضو: بيشوف الدروس المنشورة (is_published=True) بس.
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher', 'category'),
        id=group_id,
    )
    is_owner, is_member = _get_group_and_membership_or_403(request, group)

    if is_member and not is_owner and not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    if is_owner:
        lessons = group.lessons.all().order_by('order', 'created_at')
    else:
        lessons = group.lessons.filter(is_published=True).order_by('order', 'created_at')

    return render(request, 'groups/group_lessons_list.html', {
        'group': group,
        'is_owner': is_owner,
        'lessons': lessons,
    })


# ---------------------------------------------------------------------------
# Part 28: تشغيل درس واحد (المدرس صاحب الجروب + الطالب العضو)
# ---------------------------------------------------------------------------

@login_required
def watch_group_lesson(request, lesson_id):
    """
    صفحة تشغيل درس واحد. مسار المدخل بـ lesson_id بس (من غير group_id في
    الـ URL) — نفس فلسفة watch_group_recording/join_live_session (Part
    25/26): الـ view بتستنتج الجروب من الدرس نفسه مباشرة.

    نفس فحص الصلاحية المعتاد (عضوية/ownership + is_group_content_accessible
    للطالب)، بالإضافة لفحص أمان إضافي مطلوب صراحة في نص الجزء: الطالب
    (مش المدرس) مايقدرش يفتح درس لسه مش منشور (is_published=False) حتى
    لو حصل على الـ id بشكل مباشر (زي محاولة تخمين رقم متسلسل) — الفحص ده
    جوه الـ view نفسها مش بس إخفاء الدرس من القايمة، بالظبط زي ما اتطلب.
    ده كمان تجهيز لـ Part 31 (النشر التلقائي بالجدولة) اللي هيعتمد على
    نفس is_published كمصدر الحقيقة الوحيد لإتاحة الدرس.
    """
    lesson = get_object_or_404(
        GroupLesson.objects.select_related('group', 'group__teacher'),
        id=lesson_id,
    )
    group = lesson.group
    is_owner, is_member = _get_group_and_membership_or_403(request, group)

    if is_member and not is_owner and not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    if not is_owner and not lesson.is_published:
        raise Http404('الدرس ده مش متاح دلوقتي.')

    return render(request, 'groups/watch_group_lesson.html', {
        'group': group,
        'is_owner': is_owner,
        'lesson': lesson,
    })