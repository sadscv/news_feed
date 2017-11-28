#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-9 上午11:26
# @Author  : sadscv
# @File    : tasks.py

import os
import sys
from time import sleep

import scrapydo
from celery import Celery
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from crawls.news_spider.spiders.newsspider import NeteaseNewsSpider, SinaNewsSpider, SohuNewsSpider, TencentNewsSpider, \
    ZgqxbNewsSpider, XinminNewsSpider

# SPIDERS = [SohuNewsSpider, NeteaseNewsSpider, SinaNewsSpider,
SPIDERS = [TencentNewsSpider]
# SPIDERS = [NeteaseNewsSpider]
celery_app = Celery('crawls.news_spider.spiders.tasks')
celery_app.config_from_object('CONFIG.celeryconfig')
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)


def first_run(i):
    import pickle
    filehandler = open('tmpfile', 'wb')
    if i ==0:
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawls.news_spider.settings'
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        pickle.dump(process, filehandler)
    else:
        process = pickle.load(filehandler)
        process.stop()
    return process



@celery_app.task
def run_spider(i):
        print('#'*100)
        process = first_run(i)
        spider = SPIDERS[i]
        task = spider()
        process.crawl(task)
        if i ==0:
            process.start()
            #Todo(sadscv) note: CrawlerProcess().start starts a Twisted reactor
            # twisted reactor是单例模式，只能存在一个．


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
            # run_spider_react.delay(i)
            run_spider_react(i)
        sleep(300)
        # crawl()