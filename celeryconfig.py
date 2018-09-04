from __future__ import absolute_import
from celery.schedules import crontab

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis'
CELERYBEAT_SCHEDULE = {
        "every-day": {
            'task': 'tasks.add',
            # 美国时间 --> 正常时间减8小时
            'schedule': crontab(hour=4, minute=58),
        }
    }
