from __future__ import absolute_import
from celery import Celery
import celeryconfig
from spider import start
import time
app = Celery('tasks')
app.config_from_object(celeryconfig)

# 远端测试
# 拉取测试
@app.task
def add():
    start()
