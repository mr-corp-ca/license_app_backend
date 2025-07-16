import os
from celery import Celery
import multiprocessing

multiprocessing.set_start_method('spawn')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driving_license.settings')

app = Celery('driving_license')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/0',
    # broker_url='redis://127.0.0.1:6379/0',
    # result_backend='redis://127.0.0.1:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool='solo',
)