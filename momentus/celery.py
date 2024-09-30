# momentus/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'momentus.settings')

app = Celery('momentus')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'expire-subscriptions-every-day': {
        'task': 'subscriptions.tasks.expire_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Runs every day at midnight
    },
}

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Additional settings
