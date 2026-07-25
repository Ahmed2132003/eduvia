"""
groups/tasks.py
===============
Part 15 — تجميد الاشتراكات المنتهية تلقائيًا.
Part 16 — تنبيهات قبل انتهاء الاشتراك.

قرار معماري (Part 15، لسه سارٍ): استخدمت @shared_task (من celery مباشرة)
بدل ما أسيب الدالة عادية زي performance_analysis/tasks.py — الملف ده
(performance_analysis) دواله (send_dashboard_report,
send_dashboard_report_to_all) من غير أي decorator أصلاً وبيتم نداؤها
يدويًا، وده مش كافي عشان django-celery-beat/Celery beat يقدر يلاقي
التاسك بالاسم النصي المسجّل في beat_schedule. عشان كده استخدمت
@shared_task القياسية من celery نفسها لكل تاسكات groups (زي التاسك
الجديد في الجزء ده كمان)، وده أضمن طريقة تخلي التاسك discoverable فعليًا
عن طريق autodiscover_tasks() الموجودة في Eduvia/celery.py.

قرار معماري (Part 16، جديد): طريقة الإرسال بتستخدم django.core.mail.send_mail
البسيطة (بنفس نمط accounts/views.py::register_view اللي بيبعت كود
التحقق بالإيميل) بدل نمط performance_analysis/tasks.py (اللي بيبني
EmailMessage مع مرفق PDF كامل عن طريق ReportLab/generate_dashboard_report_pdf).
السبب: تنبيه انتهاء الاشتراك رسالة نصية بسيطة (تذكير + رابط) مش تقرير
مفصّل محتاج مرفق، فمفيش داعي لتعقيد generate_dashboard_report_pdf ولا
لموديل تسجيل زي PerformanceReport هنا. استخدام send_mail هو أبسط قالب
إرسال إيميل موجود بالفعل وشغال في المشروع (نفس EMAIL_BACKEND/
EMAIL_HOST_USER المظبوطين في settings.py، بدون أي إعداد إضافي).
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import GroupSubscription

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