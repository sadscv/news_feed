#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-14 下午1:05
# @Author  : sadscv
# @File    : celeryconfig.py


## Broker settings.
BROKER_URL = 'redis://localhost:6379'

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# List of modules to import when celery starts.
CELERY_IMPORTS=('crawls.news_spider.spiders.testspider', 'info_engine', 'crawls.ProxyPool.proxypool',
                'crawls.news_spider.spiders.tasks')

CELERYD_MAX_TASKS_PER_CHILD = 1

# CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}