# -*- coding: utf-8 -*-
import os

import scrapy
import sys
from celery import Celery
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
import logging

from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

logger = logging.getLogger("test spider")

celery_app = Celery('crawls.news_spider.spiders.test')
celery_app.config_from_object('CONFIG.celeryconfig')
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)


class TestSpider(scrapy.Spider):
    name = "test"

    allowed_domains = ["http://httpbin.org/"]
    website_possible_httpstatus_list = [403]
    handle_httpstatus_list = [403]
    
    start_urls = (
        'http://httpbin.org/ip',
    )

    def parse(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        print(response.body)
        req = response.request
        req.meta["change_proxy"] = True
        yield req
        # yield response.request

        # if response.body == "banned":
        #     req = response.request
        #     req.meta["change_proxy"] = True
        #     yield req
        # else:
        #     logger.info("got page: %s" % response.body)
        #     yield response.request

def run_spider():
    spider = TestSpider()

    sys.path.append(os.path.join(os.path.curdir, "crawlers/myproject"))
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawls.news_spider.settings'

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spider)
    process.start()

@celery_app.task
def crawl_test():
    return run_spider()

if __name__ == '__main__':
    crawl_test.delay()