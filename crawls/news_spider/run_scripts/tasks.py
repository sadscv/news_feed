#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-9 上午11:26
# @Author  : sadscv
# @File    : tasks.py
import os
import sys
from time import sleep

from celery import Celery
from scrapy.crawler import CrawlerProcess, CrawlerRunner, Crawler
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from crawls.news_spider.spiders.CctvNews import CctvNewsSpider
from crawls.news_spider.spiders.JndsbNews import JndsbNewsSpider
from crawls.news_spider.spiders.NeteaseNews import NeteaseNewsSpider
from crawls.news_spider.spiders.SohuNews import SohuNewsSpider
from crawls.news_spider.spiders.TencentNews import TencentNewsSpider
from crawls.news_spider.spiders.XinminNews import XinminNewsSpider
from crawls.news_spider.spiders.ZgqxbNews import ZgqxbNewsSpider

# SPIDERS = [NeteaseNewsSpider, TencentNewsSpider,
#            CctvNewsSpider, JndsbNewsSpider]
SPIDERS = [TencentNewsSpider]


celery_app = Celery('crawls.news_spider.run_scripts.tasks')
celery_app.config_from_object('CONFIG.celeryconfig')

# 以下是用celery beat定时执行任务（并不好用）
# celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)
# celery_app.conf.update(
#     CELERYBEAT_SCHEDULE={
#         'perminute': {
#             'task': 'tasks.run_spider_react',
#             'schedule': crontab(minute='*/1'),
#             'args': (0,)
#         }
#     }
# )


def UrlCrawlerScript(Process):
    def __init__(self, spider):
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(settings)
        self.crawler.configure()
        # self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)

    def run(self):
        self.crawler.crawl(self.spider)
        self.crawler.start()
        reactor.run()


@celery_app.task
def run_spider_react(i):
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawls.news_spider.settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    spider = SPIDERS[i]
    task = spider()
    process.crawl(task)
    process.start()
    print('$$$$$','start process')
            # Todo(sadscv) note: CrawlerProcess().start starts a Twisted reactor
            # twisted reactor是单例模式，只能存在一个．
        # process.queue.append_spider(task)


if __name__ == '__main__':
    while True:
        for i in range(len(SPIDERS)):
            # run_spider.delay(i)
            run_spider_react.delay(i)
            # run_spider_react(i)
        sleep(30000)
        # crawl()这是一个测试