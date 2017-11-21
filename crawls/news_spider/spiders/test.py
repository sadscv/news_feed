# -*- coding: utf-8 -*-
import os

import scrapy
import sys
from celery import Celery
from scrapy.crawler import CrawlerProcess
import logging

from scrapy.utils.project import get_project_settings

logger = logging.getLogger("test spider")

celery_app = Celery('crawls.news_spider.spiders.test')
celery_app.config_from_object('CONFIG.celeryconfig')
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

global COUNT
COUNT = 0
class TestSpider(scrapy.Spider):
    name = "test"

    allowed_domains = ["http://httpbin.org/"]
    website_possible_httpstatus_list = [403]
    handle_httpstatus_list = [403]
    
    start_urls = (
        'http://httpbin.org/ip',
    )

    def parse(self, response):
        global COUNT
        try:
            print(response.text)
        except:
            pass
        COUNT += 1
        if response.body:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            print('crawl failed')
            yield response.request


def run_spider():
    spider = TestSpider()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawls.news_spider.settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spider)
    process.start()

@celery_app.task
def crawl_test():
    return run_spider()

if __name__ == '__main__':
    # crawl_test.delay()
    run_spider()