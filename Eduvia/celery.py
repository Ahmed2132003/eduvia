import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Eduvia.settings')

app = Celery('Eduvia')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-weekly-reports': {
        'task': 'performance_analysis.tasks.send_periodic_reports',
        'schedule': crontab(day_of_week='monday', hour=8, minute=0),  # Every Monday at 8 AM
    },
    # Part 15 — نظام جروبات المناهج (Eduvia):
    # بتشتغل يوميًا الساعة 2 صباحًا (وقت هادي، بعيد عن ساعات الذروة)
    # وبتحوّل أي GroupSubscription منتهي (end_date < الآن) لـ 'expired'
    # وتجمّد الجروب المرتبط (TeacherGroup.is_active = False).
    'freeze-expired-group-subscriptions': {
        'task': 'groups.tasks.freeze_expired_group_subscriptions',
        'schedule': crontab(hour=2, minute=0),
    },
    # Part 16 — نظام جروبات المناهج (Eduvia):
    # بتشتغل يوميًا الساعة 9 صباحًا (بعد ساعتين من تاسك التجميد بتاع
    # Part 15، عشان أي اشتراك اتجمد فعليًا يبقى status='expired' قبل ما
    # تاسك التنبيهات يعدي عليه — التاسك أصلاً بيفلتر على status='active'
    # بس فمش هيبعت تنبيه لاشتراك اتجمد بالفعل، لكن الفصل الزمني ده منطقي
    # أكتر وبيقلل أي تداخل نظري بين التاسكين). الساعة 9 صباحًا كمان وقت
    # مناسب أكتر من 2 فجرًا لإرسال تنبيه للمدرس (وقت شغل، مش نص الليل).
    # بتبعت تنبيه عادي لكل اشتراك active هيخلص خلال 3 أيام، وتنبيه أشد
    # لهجة لما يتبقى يوم واحد بس — بمنطق منع التكرار الموضح في
    # groups/tasks.py::send_subscription_expiry_reminders.
    'send-subscription-expiry-reminders': {
        'task': 'groups.tasks.send_subscription_expiry_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
}