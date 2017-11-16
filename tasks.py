#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-9 上午11:26
# @Author  : sadscv
# @File    : tasks.py

import os
import sys

from celery import Celery
from celery.utils.log import get_task_logger
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


from crawls.news_spider.spiders.newsspider import NeteaseNewsSpider, SinaNewsSpider


# app = Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app = Celery('tasks')
celery_app.config_from_object('CONFIG.celeryconfig')
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

# logger = get_task_logger(__name__)


def run_spider():
    spider = NeteaseNewsSpider()
    # spider = SinaNewsSpider()
    # settings = Settings(
    #     {
    #         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    #         'ITEM_PIPELINES': {
    #             'crawls.news_spider.pipelines.NewsSpiderPipeline': 300,
    #         }
    #     })
    # sys.path.append(os.path.join(os.path.curdir, "crawlers/myproject"))
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawls.news_spider.settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spider)
    process.start()
    # crawler.join()


@celery_app.task
def crawl():
    return run_spider()



if __name__ == '__main__':
    # crawl.delay()
    crawl()