"""
groups/tasks.py
===============
Part 15 — تجميد الاشتراكات المنتهية تلقائيًا.
Part 16 — تنبيهات قبل انتهاء الاشتراك.
Part 31 (المرحلة الثانية) — نشر الدروس المجدولة (GroupLesson) تلقائيًا في مواعيدها.
Part 36 (المرحلة الثانية) — تذكيرات المهام (GroupTodoItem) اللي قرب معادها.

قرار معماري (Part 15، لسه سارٍ): استخدمت @shared_task (من celery مباشرة)
بدل ما أسيب الدالة عادية زي performance_analysis/tasks.py — الملف ده
(performance_analysis) دواله (send_dashboard_report,
send_dashboard_report_to_all) من غير أي decorator أصلاً وبيتم نداؤها
يدويًا، وده مش كافي عشان django-celery-beat/Celery beat يقدر يلاقي
التاسك بالاسم النصي المسجّل في beat_schedule. عشان كده استخدمت
@shared_task القياسية من celery نفسها لكل تاسكات groups (زي التاسك
الجديد في الجزء ده كمان)، وده أضمن طريقة تخلي التاسك discoverable فعليًا
عن طريق autodiscover_tasks() الموجودة في Eduvia/celery.py.

قرار معماري (Part 16، لسه سارٍ): طريقة الإرسال بتستخدم django.core.mail.send_mail
البسيطة (بنفس نمط accounts/views.py::register_view اللي بيبعت كود
التحقق بالإيميل) بدل نمط performance_analysis/tasks.py (اللي بيبني
EmailMessage مع مرفق PDF كامل). نفس الأسلوب اتبع هنا في Part 31 لإرسال
إشعار الدرس الجديد — زي ما اتطلب صراحة ("استخدم نفس نظام الإشعارات اللي
استخدمته في Part 16").

قرار معماري (Part 31، جديد):
- ما فيش أي تعديل على GroupLesson/models — الحقلين is_published وpublish_at
  كانوا موجودين بالفعل من Part 27، والفورم اللي بيملاهم (اختيار "انشر
  دلوقتي"/"جدولة") كان اتعمل بالفعل مقدّمًا في Part 28
  (groups/views_lessons.py::upload_group_lesson) — يعني نقطة 1 من متطلبات
  الجزء ده كانت متحققة بالفعل قبل ما نوصل لـ Part 31 رسميًا، فمفيش أي
  تعديل مطلوب في الفورم أو التمبلت هنا.
- نفس الشيء لنقطة 4 (منع فتح رابط الدرس مباشرة قبل النشر) — كانت متحققة
  بالفعل في groups/views_lessons.py::watch_group_lesson من Part 28
  (فحص `if not is_owner and not lesson.is_published: raise Http404`).
  الجزء ده (31) بيضيف بس الطبقة الناقصة: التاسك الدوري نفسه + الإشعارات.
- الإشعار بيتبعت لكل أعضاء الجروب (GroupMembership.student) اللي ليهم
  إيميل مسجّل — بنفس منطق الحماية من Part 16 (`_send_expiry_reminder_email`):
  لو طالب معندوش إيميل، بيتسجّل تحذير ويتخطى بدل ما يوقف باقي الإرسال.
  كل عملية إرسال لكل طالب متلفوفة في try/except منفصلة (زي منطق Part 16
  بالحرف) — لو إرسال لطالب واحد فشل، باقي أعضاء الجروب هياخدوا إشعارهم
  عادي.
- التاسك بيشتغل كل 5 دقايق (Eduvia/celery.py) — رقم اخترته بنفسي، مفيش
  تحديد صريح في الطلب الأصلي غير "مثلاً" كل 5 دقايق. سهل التعديل لو
  Ahmed عايز فترة مختلفة.

قرار معماري (Part 36، جديد):
- كررت نفس منطق send_subscription_expiry_reminders (Part 16) بالظبط:
  فلاج واحد (reminder_sent على GroupTodoItem، Part 36) بيمنع تكرار
  الإرسال، helper داخلي منفصل لبناء/إرسال الإيميل (_send_todo_reminder_email)،
  وtask دورية (@shared_task) بتفلتر وترسل مع try/except لكل مهمة على حدة
  (لو فشل تذكير مهمة واحدة، باقي المهام في نفس التشغيلة بتكمل عادي).
- "قريب" اتفسّرت كـ نافذة ساعة واحدة قدام (0 < due_at - الآن <= ساعة)،
  زي الاقتراح الحرفي في نص الطلب ("خلال ساعة مثلاً"). التاسك بيشتغل كل
  10 دقايق (Eduvia/celery.py) — رقم اخترته بنفسي (مفيش تحديد صريح في
  الطلب)، توازن بين دقة كافية (المهمة تاخد تذكيرها قريب من دخولها
  النافذة) ومعدل استعلامات معقول، مقارنة بالـ 5 دقايق المستخدمة في نشر
  الدروس (Part 31 — هناك التوقيت أدق أهمية لأن الدرس نفسه المفروض ينزل،
  هنا التذكير مجرد تنبيه وقتي أوسع شوية مقبول).
- مفيش فحص لحالة الجروب (is_group_content_accessible) هنا — المهمة
  ملكها owner واحد بس (شخصية بالكامل حتى لو مرتبطة بجروب)، فمفيش أي
  علاقة بصلاحيات محتوى الجروب المستخدمة في باقي أجزاء المرحلة الثانية.
- الفلتر (نفس فلسفة نافذة "خلال 3 أيام" في Part 16 بالحرف، بس بساعة
  بدل أيام): due_at لسه في المستقبل ومش بعيد أكتر من ساعة
  (0 < due_at - الآن <= ساعة، يعني due_at__gt=الآن وdue_at__lte=الآن+ساعة)،
  is_done=False، وreminder_sent=False. مهمة فات معادها بالفعل (due_at
  في الماضي) مش بتاخد تذكير جديد هنا — دي بقت "متأخرة" (overdue) وليها
  تمييز بصري منفصل في my_todo_list.html (متطلب 3، كان أصلاً متطبق من
  Part 35)، مش تذكير بالإيميل.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import GroupLesson, GroupSubscription, GroupTodoItem

logger = logging.getLogger(__name__)


@shared_task
def freeze_expired_group_subscriptions():
    """
    Part 15.

    بتدور على كل GroupSubscription بحالة status='active' وend_date
    اتخطى الوقت الحالي، وتحوّلها لـ status='expired'، وتجمّد الجروب
    المرتبط (TeacherGroup.is_active = False).

    ملحوظة مهمة: تحديث is_active هنا هو بس للعرض السريع (لوحة تحكم
    المدرس، إلخ) — المصدر الحقيقي لـ "هل محتوى الجروب متاح دلوقتي؟" هو
    groups.access.is_group_content_accessible(group)، اللي بيتأكد
    مباشرة من وجود اشتراك active سارٍ، مش من الفلاج ده لوحده. يعني حتى
    لو التاسك ده اتأخر يوم في التشغيل لأي سبب، is_group_content_accessible
    هيرجع False صح على أي حال لأي جروب اشتراكه خلص، والفلاج هيتظبط لاحقًا
    أول ما التاسك يشتغل.
    """
    now = timezone.now()
    expired_subscriptions = GroupSubscription.objects.select_related('group').filter(
        status='active',
        end_date__lt=now,
    )

    expired_count = 0
    for subscription in expired_subscriptions:
        subscription.status = 'expired'
        subscription.save(update_fields=['status'])

        group = subscription.group
        if group.is_active:
            group.is_active = False
            group.save(update_fields=['is_active'])

        expired_count += 1

    logger.info(
        "freeze_expired_group_subscriptions: expired %s subscription(s)",
        expired_count,
    )
    return expired_count


def _send_expiry_reminder_email(subscription, urgent=False):
    """
    Part 16: helper داخلي بس (مش task) بيبني ويبعت إيميل التنبيه لمدرس
    معين عن اشتراك جروب واحد. urgent=True بيغيّر العنوان واللهجة للتنبيه
    الأشد (يوم واحد متبقي).

    لو المدرس معندوش إيميل مسجّل (نظريًا مينفعش يحصل لأن التسجيل بيتطلب
    إيميل، لكن كطبقة حماية إضافية)، بيتخطى الإرسال ويسجّل تحذير بدل ما
    يرمي Exception يوقف باقي التاسك.
    """
    teacher = subscription.group.teacher
    if not teacher.email:
        logger.warning(
            "_send_expiry_reminder_email: skipped subscription %s - teacher %s has no email",
            subscription.id, teacher.username,
        )
        return False

    group_display_name = str(subscription.group)
    end_date_str = subscription.end_date.strftime('%Y-%m-%d %H:%M') if subscription.end_date else 'غير محدد'

    if urgent:
        subject = f'تنبيه عاجل: اشتراك جروب "{group_display_name}" هيخلص بكرة!'
        body = (
            f'مرحبًا {teacher.username}،\n\n'
            f'اشتراك جروبك "{group_display_name}" هيخلص خلال يوم واحد بس (بتاريخ {end_date_str}).\n'
            'لو ما جددتش الاشتراك، الجروب هيتجمد أوتوماتيك وطلابك مش هيقدروا '
            'يوصلوا لمحتواه (الحصص اللايف والشات) لحد ما تجدد.\n\n'
            'اذهب للوحة تحكم المدرس دلوقتي عشان تجدد الاشتراك.\n\n'
            'فريق Eduvia'
        )
    else:
        subject = f'تذكير: اشتراك جروب "{group_display_name}" هيخلص قريبًا'
        body = (
            f'مرحبًا {teacher.username}،\n\n'
            f'اشتراك جروبك "{group_display_name}" هيخلص خلال 3 أيام (بتاريخ {end_date_str}).\n'
            'ننصحك تجدد الاشتراك قبل الموعد ده عشان تضمن استمرارية الوصول '
            'لمحتوى الجروب لطلابك من غير أي انقطاع.\n\n'
            'فريق Eduvia'
        )

    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [teacher.email],
        fail_silently=False,
    )
    return True


@shared_task
def send_subscription_expiry_reminders():
    """
    Part 16.

    Celery task يومية بتبعت تنبيهين مستقلين للمدرسين اللي اشتراكات
    جروباتهم النشطة قربت تخلص:

    1) تنبيه عادي: لكل GroupSubscription بحالة status='active' وend_date
       هيجي خلال 3 أيام أو أقل (لسه ماخلصش)، لو reminder_3days_sent لسه
       False. بعد الإرسال بيتحط True عشان مايتكررش.

    2) تنبيه عاجل (أشد لهجة): لكل GroupSubscription بحالة status='active'
       وend_date هيجي خلال يوم واحد أو أقل (لسه ماخلصش)، لو
       reminder_1day_sent لسه False. بعد الإرسال بيتحط True عشان
       مايتكررش.

    التنبيهين مستقلين تمامًا عن بعض (اشتراك ممكن ياخد الاتنين بالترتيب
    الطبيعي مع اقتراب end_date، أو ياخد واحد بس لو التاسك اتشغل لأول مرة
    وend_date قريب أصلاً من البداية) — الفحص بيعتمد بس على "الفلاج ده
    اتبعت قبل كده ولا لأ"، مش على تاريخ إرسال آخر مرة، عشان يفضل بسيط
    وواضح.

    التاسك ده منفصل تمامًا عن freeze_expired_group_subscriptions (Part
    15) وبيشتغل في وقت تاني (تفاصيل الجدولة في Eduvia/celery.py) — مفيش
    أي تعديل على تاسك التجميد نفسه.
    """
    now = timezone.now()

    # ── التنبيه العادي: هيخلص خلال 3 أيام ──
    three_days_from_now = now + timedelta(days=3)
    soon_expiring_3days = GroupSubscription.objects.select_related(
        'group', 'group__teacher'
    ).filter(
        status='active',
        end_date__isnull=False,
        end_date__gt=now,
        end_date__lte=three_days_from_now,
        reminder_3days_sent=False,
    )

    sent_3days = 0
    for subscription in soon_expiring_3days:
        try:
            _send_expiry_reminder_email(subscription, urgent=False)
            subscription.reminder_3days_sent = True
            subscription.save(update_fields=['reminder_3days_sent'])
            sent_3days += 1
        except Exception:
            logger.exception(
                "send_subscription_expiry_reminders: failed to send 3-day reminder for subscription %s",
                subscription.id,
            )

    # ── التنبيه العاجل: هيخلص خلال يوم واحد ──
    one_day_from_now = now + timedelta(days=1)
    soon_expiring_1day = GroupSubscription.objects.select_related(
        'group', 'group__teacher'
    ).filter(
        status='active',
        end_date__isnull=False,
        end_date__gt=now,
        end_date__lte=one_day_from_now,
        reminder_1day_sent=False,
    )

    sent_1day = 0
    for subscription in soon_expiring_1day:
        try:
            _send_expiry_reminder_email(subscription, urgent=True)
            subscription.reminder_1day_sent = True
            subscription.save(update_fields=['reminder_1day_sent'])
            sent_1day += 1
        except Exception:
            logger.exception(
                "send_subscription_expiry_reminders: failed to send 1-day reminder for subscription %s",
                subscription.id,
            )

    logger.info(
        "send_subscription_expiry_reminders: sent %s 3-day reminder(s) and %s 1-day reminder(s)",
        sent_3days, sent_1day,
    )
    return {'sent_3days': sent_3days, 'sent_1day': sent_1day}


def _notify_group_members_new_lesson(lesson):
    """
    Part 31: helper داخلي بس (مش task) بيبعت إيميل لكل أعضاء الجروب
    (GroupMembership.student) يبلغهم إن درس جديد نزل، بنفس أسلوب
    _send_expiry_reminder_email (Part 16) بالظبط — نفس نظام الإشعارات
    (send_mail بسيط)، نفس منطق تخطي الطلاب اللي معندهمش إيميل مع تسجيل
    تحذير بدل ما نوقف العملية.

    بترجع عدد الإشعارات اللي اتبعتت بنجاح فعليًا.
    """
    group = lesson.group
    group_display_name = str(group)

    subject = f'درس جديد نزل في جروب "{group_display_name}"'
    body = (
        f'درس جديد "{lesson.title}" نزل دلوقتي في جروبك "{group_display_name}".\n\n'
        'ادخل على المنصة دلوقتي عشان تشوفه.\n\n'
        'فريق Eduvia'
    )

    sent_count = 0
    memberships = group.memberships.select_related('student').all()
    for membership in memberships:
        student = membership.student
        if not student.email:
            logger.warning(
                "_notify_group_members_new_lesson: skipped student %s - no email (lesson %s)",
                student.username, lesson.id,
            )
            continue
        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception:
            logger.exception(
                "_notify_group_members_new_lesson: failed to notify student %s for lesson %s",
                student.username, lesson.id,
            )

    return sent_count


@shared_task
def publish_scheduled_group_lessons():
    """
    Part 31 (المرحلة الثانية).

    Celery task دورية (كل 5 دقايق — تفاصيل الجدولة في Eduvia/celery.py)
    بتدور على كل GroupLesson بحالة is_published=False وpublish_at محدد
    ووصل معاده (publish_at <= الآن)، وتحوّلها is_published=True، وتبعت
    إشعار لكل أعضاء الجروب المرتبط.

    الفحص is_published=False كافي وحده — مفيش أي درس is_published=True
    ليه publish_at في نفس الوقت (الفورم في Part 28 بيحط is_published=True
    وpublish_at=None في حالة "انشر دلوقتي"، وis_published=False +
    publish_at محدد في حالة "جدولة") — لكن ضفت شرط publish_at__isnull=False
    كطبقة حماية إضافية بسيطة، عشان لو أي درس is_published=False من غير
    publish_at (نظريًا مش متوقع يحصل من الفورم الحالي) ميتنشرش غلط من
    غير ميعاد محدد.

    كل درس بيتنشر لوحده جوه try/except منفصل (نفس فلسفة Part 16) — لو
    فشل إرسال الإشعارات لدرس معين لأي سبب، باقي الدروس المستحقة في نفس
    التشغيلة بتكمل عادي وميتأثروش.
    """
    now = timezone.now()
    due_lessons = GroupLesson.objects.select_related(
        'group', 'group__teacher', 'group__category'
    ).filter(
        is_published=False,
        publish_at__isnull=False,
        publish_at__lte=now,
    )

    published_count = 0
    for lesson in due_lessons:
        try:
            lesson.is_published = True
            lesson.save(update_fields=['is_published'])
            _notify_group_members_new_lesson(lesson)
            published_count += 1
        except Exception:
            logger.exception(
                "publish_scheduled_group_lessons: failed to publish lesson %s",
                lesson.id,
            )

    logger.info(
        "publish_scheduled_group_lessons: published %s lesson(s)",
        published_count,
    )
    return published_count


# ---------------------------------------------------------------------------
# Part 34 (المرحلة الثانية): إشعار الطالب بتصحيح واجبه
# ---------------------------------------------------------------------------

def _notify_student_assignment_graded(submission):
    """
    Part 34: helper داخلي بس (مش @shared_task) بيبعت إيميل للطالب لما
    المدرس يصحح تسليمه، بنفس أسلوب _send_expiry_reminder_email (Part 16)
    و_notify_group_members_new_lesson (Part 31) بالظبط — نفس نظام
    الإشعارات (send_mail بسيط)، نفس منطق تخطي المستخدم اللي معندوش
    إيميل مع تسجيل تحذير بدل ما نوقف العملية.

    القرار (مش @shared_task): التصحيح فعل لحظي بيحصل جوه request واحد
    (المدرس بيصحح تسليم واحد بالظبط)، مش عملية دورية بتمشي على مجموعة
    سجلات زي send_subscription_expiry_reminders أو
    publish_scheduled_group_lessons — فمفيش داعي لتاسك Celery منفصل هنا،
    نفس فلسفة منح XP الفوري (synchronous) من Part 17. بترجع True/False
    عشان الـ caller (grade_submissions view) يقدر يعرف نجح الإرسال ولا
    لأ لو حابب يستخدم القيمة مستقبلًا (مش مستخدمة دلوقتي).
    """
    student = submission.student
    if not student.email:
        logger.warning(
            "_notify_student_assignment_graded: skipped submission %s - student %s has no email",
            submission.id, student.username,
        )
        return False

    assignment = submission.assignment
    group_display_name = str(assignment.group)

    subject = f'واجبك في "{assignment.title}" اتصحح'
    body = (
        f'مرحبًا {student.username}،\n\n'
        f'واجبك في "{assignment.title}" (جروب "{group_display_name}") اتصحح، '
        f'درجتك: {submission.grade} من {assignment.max_grade}.\n\n'
        + (f'ملاحظات المدرس: {submission.feedback}\n\n' if submission.feedback else '')
        + 'ادخل على المنصة عشان تشوف التفاصيل كاملة.\n\n'
        'فريق Eduvia'
    )

    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [student.email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception(
            "_notify_student_assignment_graded: failed to notify student %s for submission %s",
            student.username, submission.id,
        )
        return False


# ---------------------------------------------------------------------------
# Part 36 (المرحلة الثانية): تذكيرات المهام (GroupTodoItem) اللي قرب معادها
# ---------------------------------------------------------------------------

def _send_todo_reminder_email(todo):
    """
    Part 36: helper داخلي بس (مش @shared_task) بيبني ويبعت إيميل تذكير
    لصاحب المهمة (owner) — نفس أسلوب _send_expiry_reminder_email (Part 16)
    و_notify_group_members_new_lesson (Part 31) بالظبط: send_mail بسيط،
    ولو المستخدم معندوش إيميل مسجّل، بيتخطى الإرسال ويسجّل تحذير بدل ما
    يرمي Exception يوقف باقي التاسك.
    """
    owner = todo.owner
    if not owner.email:
        logger.warning(
            "_send_todo_reminder_email: skipped todo %s - owner %s has no email",
            todo.id, owner.username,
        )
        return False

    due_at_str = todo.due_at.strftime('%Y-%m-%d %H:%M') if todo.due_at else 'غير محدد'
    group_line = f' (جروب "{todo.group}")' if todo.group_id else ''

    subject = f'تذكير: مهمة "{todo.title}" قرب معادها'
    body = (
        f'مرحبًا {owner.username}،\n\n'
        f'مهمتك "{todo.title}"{group_line} قرب معادها (بتاريخ {due_at_str}).\n'
        + (f'ملاحظات: {todo.notes}\n\n' if todo.notes else '\n')
        + 'ادخل على المنصة عشان تشوف قايمة مهامك.\n\n'
        'فريق Eduvia'
    )

    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [owner.email],
        fail_silently=False,
    )
    return True


@shared_task
def send_todo_reminders():
    """
    Part 36 (المرحلة الثانية).

    Celery task دورية (كل 10 دقايق — تفاصيل الجدولة في Eduvia/celery.py)
    بتدور على كل GroupTodoItem لسه is_done=False وreminder_sent=False
    ومعادها (due_at) قرب خلال ساعة (لسه في المستقبل، مش أبعد من ساعة من
    دلوقتي)، وتبعت تذكير لصاحبها عن طريق _send_todo_reminder_email، وتحط
    reminder_sent=True بعد نجاح الإرسال عشان مايتكررش (نفس منطق
    reminder_3days_sent/reminder_1day_sent من Part 16 بالحرف).

    كل مهمة بتتعالج جوه try/except منفصل (نفس فلسفة كل تاسكات groups
    التانية) — لو فشل تذكير مهمة واحدة، باقي المهام المستحقة في نفس
    التشغيلة بتكمل عادي وميتأثروش.
    """
    now = timezone.now()
    one_hour_from_now = now + timedelta(hours=1)

    due_soon_todos = GroupTodoItem.objects.select_related('owner', 'group').filter(
        is_done=False,
        reminder_sent=False,
        due_at__isnull=False,
        due_at__gt=now,
        due_at__lte=one_hour_from_now,
    )

    sent_count = 0
    for todo in due_soon_todos:
        try:
            _send_todo_reminder_email(todo)
            todo.reminder_sent = True
            todo.save(update_fields=['reminder_sent'])
            sent_count += 1
        except Exception:
            logger.exception(
                "send_todo_reminders: failed to send reminder for todo %s",
                todo.id,
            )

    logger.info(
        "send_todo_reminders: sent %s reminder(s)",
        sent_count,
    )
    return sent_count