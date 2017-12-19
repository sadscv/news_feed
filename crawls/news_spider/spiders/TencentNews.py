#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:17
# @Author  : sadscv
# @File    : TencentNews.py
import json
import re

from scrapy import Request
from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



class TencentNewsSpider(CrawlSpider):
    name = 'tencent_news_spider'
    allowed_domains = ['news.qq.com']
    website_possible_httpstatus_list = [502, 404, 403, 301, 302, 429]
    start_urls = ['http://news.qq.com']
    # http://news.qq.com/a/20170825/026956.htm
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()'):
            title = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()').extract()[0]
        elif sel.xpath('//*[@id="C-Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()'):
            title = sel.xpath('//*[@id="C-Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()').extract()[0]
        elif sel.xpath('//*[@id="ArticleTit"]/text()'):
            title = sel.xpath('//*[@id="ArticleTit"]/text()').extract()[0]
        else:
            title = 'unknown'
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] + '/' + date[6:]
        newsId = pattern.group(3)
        url = response.url
        if sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/div/div[1]/span[3]/text()'):
            time_ = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/div/div[1]/span[3]/text()').extract()[0]
        else:
            time_ = 'unknown'
        contents = ListCombiner(sel.xpath('//p/text()').extract()[:-8])

        if response.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()'):
            cmt = response.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()').extract()[0]
            if re.findall(r'cmt_id = (\d*);', cmt):
                cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
                comment_url = 'http://coral.qq.com/article/{}/comment?commentid=0&reqnum=1&tag=&callback=mainComment&_=1389623278900'.format(cmt_id)

                yield Request(comment_url, self.parse_comment, meta={'source': self.name,
                                                                     'date': date,
                                                                     'newsId': newsId,
                                                                     'url': url,
                                                                     'title': title,
                                                                     'contents': contents,
                                                                     'time': time_
                                                                     })
            else:
                item = NewsItem()
                item['source'] = source
                item['time'] = time_
                item['date'] = date
                item['contents'] = contents
                item['title'] = title
                item['url'] = url
                item['newsId'] = newsId
                item['comments'] = 0
                yield item

    def parse_comment(self, response):
        if re.findall(r'"total":(\d*)\,', response.text):
            comments = re.findall(r'"total":(\d*)\,', response.text)[0]
        else:
            comments = 0
        item = NewsItem()
        item['source'] = response.meta['source']
        item['time'] = response.meta['time']
        item['date'] = response.meta['date']
        item['contents'] = response.meta['contents']
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['newsId'] = response.meta['newsId']
        item['comments'] = comments
        return item