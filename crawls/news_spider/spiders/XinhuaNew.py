#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:22
# @Author  : sadscv
# @File    : XinhuaNew.py
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner


# 新华网  successful
class XinhuaNewSpider(CrawlSpider):
    name = "xinhua_news_spider"
    start_urls = ['http://www.xinhuanet.com']
    allowed_domains = ['xinhuanet.com']
    #http: // news.xinhuanet.com / world / 2017 - 11 / 15 / c_1121956528.htm
    url_pattern = r'(http://news.xinhuanet.com)/([a-z]+)/\d{4}-(\d{1,2})/\d{1,2}/c\_(\d+)\.htm'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self,response):
        sel = Selector(response)
        # pattern = re.match(self.url_pattern, str(response.url))
        source = 'xinhuanet.com'
        if sel.xpath('//div[@class="h-info"]/span/text()'):
            time = sel.xpath('//div[@class="h-info"]/span/text()').extract_first().split()[0] + ' ' + sel.xpath('//div[@class="h-info"]/span/text()').extract_first().split()[1]
        else:
            time = 'unknown'
        # date = '20' + pattern.group(3)[0:4] + '/' + pattern.group(3)[5:]  + pattern.group(4)
        date = time.split()[0]
        title = sel.xpath('//div[@class="h-title"]/text()').extract()[0].split()
        url = response.url
        newsId = re.findall(r'c_(.*?).htm', url, re.S)[0]
        contents = ListCombiner(sel.xpath('//div[@id="p-detail"]/p/text()').extract())
        comments = 0
        item = NewsItem()
        item['source'] = self.name
        item['time'] = time
        item['date'] = date
        item['title'] = title
        item['contents'] = contents
        item['newsId'] = newsId
        item['url'] = url
        item['comments'] = comments
        yield item
