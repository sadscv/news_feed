#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-9 上午11:26
# @Author  : sadscv
# @File    : tasks.py
# from billiard.process import Process
from celery import Celery
from celery.utils.log import get_task_logger
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

from config import CELERY_BROKER, CELERY_BACKEND, CRAWL_INTERVAL
from crawls.news_spider.spiders.newsspider import NeteaseNewsSpider

app = Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)
app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

logger = get_task_logger(__name__)


# process = CrawlerProcess(get_project_settings())
#
# process.crawl('netease_news_spider', domain='news.163.com')
# process.start()



# class UrlCrawlerScript(Process):
#     def __init__(self, spider):
#         # Process.__init__(self)
#         # settings = get_project_settings()
#         self.crawler = CrawlerProcess(get_project_settings())
#         # self.crawler.configure()
#         # self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
#         self.spider = spider
#
#     def run(self):
#         self.crawler.crawl(self.spider)
#         self.crawler.start()
#         # reactor.run()

def run_spider():
    spider = NeteaseNewsSpider()
    settings = Settings(
        {
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'ITEM_PIPELINES': {
                'crawls.news_spider.pipelines.NewsSpiderPipeline': 300,
            }
        })
    process = CrawlerProcess(settings)
    process.crawl(spider)
    process.start()
    # crawler.join()


@app.task
def crawl():
    return run_spider()



if __name__ == '__main__':
    crawl.delay()