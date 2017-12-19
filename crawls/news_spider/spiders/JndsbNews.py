#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:23
# @Author  : sadscv
# @File    : JndsbNews.py
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



# 江南都市报 successful
class JndsbNewsSpider(CrawlSpider):
    name = "jndsb_news_spider"
    allowed_domains = ['jndsb.jxnews.com.cn']
    start_urls = ['http://jndsb.jxnews.com.cn']
    # http://jndsb.jxnews.com.cn/system/2017/06/17/016210714.shtml
    url_pattern = r'(http://jndsb\.jxnews\.com\.cn)/system/(\d{4})/(\d{2})/(\d{2})/(\d+)\.shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2) + '/' + pattern.group(3) + '/' + pattern.group(4)
        if sel.xpath('//span[@id="pubtime_baidu"]/text()'):
            time = sel.xpath('//span[@id="pubtime_baidu"]/text()').extract_first().split()
        else:
            time = "unknown"
        title = sel.xpath('//div[@class="BiaoTi"]/text()').extract()
        url = response.url
        newsId = pattern.group(5)
        contents = ListCombiner(sel.xpath('//div[@class="Content"]/p/text()').extract())
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