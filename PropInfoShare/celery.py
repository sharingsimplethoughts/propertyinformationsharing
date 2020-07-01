
from __future__ import absolute_import
import os
from celery import Celery
from .settings import INSTALLED_APPS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PropInfoShare.settings')

app = Celery('PropInfoShare', backend='amqp', broker='amqp://')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: INSTALLED_APPS)
