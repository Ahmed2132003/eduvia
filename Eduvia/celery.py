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
}