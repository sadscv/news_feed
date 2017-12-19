#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:05
# @Author  : zjms, sadscv
# @File    : XinminNewsSpider.py

#新民网   successful
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner


class XinminNewsSpider(CrawlSpider):
    name = "xinmin_news_spider"
    allowed_domains = ['xinmin.cn']
    start_urls = ['http://www.xinmin.cn']
    #http://edu.xinmin.cn/tt/2017/11/15/31334031.html
    #http://newsxmwb.xinmin.cn/world/2017/11/21/31335695.html
    url_pattern = r'(http://.*\.xinmin\.cn)/.*/(\d{4})/(\d{2})/(\d{2})/(\d+).html'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
        ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2) + '/' + pattern.group(3) + '/' + pattern.group(4)
        newsId = pattern.group(5)
        if sel.xpath('//div[@class="info"]/span/text()'):
            time = sel.xpath('//div[@class="info"]/span/text()').extract()[-1]
        elif sel.xpath('//span[@class="page_time"]/text()'):
            time = sel.xpath('//span[@class="page_time"]/text()').extract()
        else:
            time = "unknown"
        if sel.xpath('//h1[@class="article_title"]/text()'):
            title = sel.xpath('//h1[@class="article_title"]/text()').extract()
        elif sel.xpath('//h3[@class="content_title"]/text()'):
            title = sel.xpath('//h3[@class="content_title"]/text()').extract()
        else:
            title = "unknown"
        url = response.url
        contents = ListCombiner(sel.xpath('//div[@class="a_p"]/p/text()').extract())
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
