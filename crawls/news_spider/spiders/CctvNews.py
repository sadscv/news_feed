#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:24
# @Author  : sadscv
# @File    : CctvNews.py
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



# 央视新闻 successful
class CctvNewsSpider(CrawlSpider):
    name = "cctv_news_spider"
    allowed_domains = ['news.cctv.com']
    start_urls = ['http://news.cctv.com']
    # http: // jiankang.cctv.com / 2017 / 11 / 17 / ARTIsSTfqrpnb6Nj2UZydIXo171117.shtml
    # http: // tv.cctv.com / 2017 / 11 / 19 / VIDELf9eHnwFxj0h0p77qwNV171119.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.cctv\.com)/(\d{4})/(\d{2})/(\d{2})/(\w+)\.shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2) + '/' + pattern.group(3) + '/' + pattern.group(4)
        newsId = pattern.group(5)
        if sel.xpath('//span[@class="info"]/i/text()'):
            time = sel.xpath('//span[@class="info"]/i/text()').extract()
        elif sel.xpath('//span[@class="time"]/text()'):
            time = sel.xpath('//span[@class="time"]/text()').extract()
        else:
            time = "unknown"
        if sel.xpath('//div[@class="cnt_bd"]/h1/text()'):
            title = sel.xpath('//div[@class="cnt_bd"]/h1/text()').extract()
        elif sel.xpath('//h3[@class="title"]/text()'):
            title = sel.xpath('//h3[@class="title"]/text()').extract()
        else:
            title = "unknown"
        url = response.url
        contents = ListCombiner(sel.xpath('//div[@class="cnt_bd"]/p/text()').extract())
        comments = 0

        item = NewsItem()
        item['source'] = self.name
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item



