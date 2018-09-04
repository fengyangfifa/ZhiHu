from __future__ import absolute_import
from celery import Celery
import celeryconfig
from spider import start
import time
app = Celery('tasks')
app.config_from_object(celeryconfig)

@app.task
def add():
    start()
