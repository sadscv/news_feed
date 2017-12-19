#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:15
# @Author  : sadscv
# @File    : Sina_Spider.py
import json
import re

import time
from scrapy import Request
from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



class SinaNewsSpider(CrawlSpider):
    name = "sina_news_spider"
    allowed_domains = ['news.sina.com.cn']
    start_urls = ['http://news.sina.com.cn']
    # http://finance.sina.com.cn/review/hgds/2017-08-25/doc-ifykkfas7684775.shtml
    today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    url_pattern = r'(http://(?:\w+\.)*news\.sina\.com\.cn)/.*/({})/doc-(.*)\.shtml'.format(today_date)

    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath("//h1[@id='artibodyTitle']/text()"):
            title = sel.xpath("//h1[@id='artibodyTitle']/text()").extract()[0]
            pattern = re.match(self.url_pattern, str(response.url))
            source = pattern.group(1)
            date = pattern.group(2).replace('-','/')
            if sel.xpath('//span[@class="time-source"]/text()'):
                time_ = sel.xpath('//span[@class="time-source"]/text()').extract_first().split()[0]
            else:
                time_ = 'unknown'
            newsId = pattern.group(3)
            url = response.url
            contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
            comment_elements = sel.xpath("//meta[@name='sudameta']").xpath('@content').extract()[1]
            comment_channel = comment_elements.split(';')[0].split(':')[1]
            comment_id = comment_elements.split(';')[1].split(':')[1]
            comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={}&newsid={}'.format(comment_channel,comment_id)

            yield Request(comment_url, self.parse_comment, meta={'source':self.name,
                                                                 'date':date,
                                                                 'newsId':newsId,
                                                                 'url':url,
                                                                 'title':title,
                                                                 'contents':contents,
                                                                 'time':time_
                                                                })

    def parse_comment(self, response):
        if re.findall(r'"total": (\d*)\,', response.text):
            comments = re.findall(r'"total": (\d*)\,', response.text)[0]
        else:
            comments = 0
        item = NewsItem()
        item['comments'] = comments
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = response.meta['contents']
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        return item
