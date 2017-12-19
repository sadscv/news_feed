#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:11
# @Author  : sadscv
# @File    : Netease_Spider.py
import json
import re

from scrapy import Request
from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



class NeteaseNewsSpider(CrawlSpider):
    website_possible_httpstatus_list = [404, 403, 301]
    name = "netease_news_spider"
    start_urls = ['http://news.163.com/']
    # Spider中间件会对Spider发出的request进行检查，只有满足allow_domain才会被允许发出
    allowed_domains = ['news.163.com']


    # http://news.163.com/17/0823/20/CSI5PH3Q000189FH.html
    # 诸如 http://news.163.com/16/0602/16/BOIMS8PF00014JB5.htm0 这样的链接能够通过url_patten.
    url_pattern = r'(http://news\.163\.com)/(\d{2})/(\d{4})/\d+/(\w+)\.html'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    '''
    1. 因为使用的yield，而不是return。parse函数将会被当做一个生成器使用。scrapy会逐一获取parse方法中生成的结果，并判断该结果是一个什么样的类型；
    2. 如果是request则加入爬取队列，如果是item类型则使用pipeline处理，其他类型则返回错误信息。
    3. scrapy取到第一部分的request不会立马就去发送这个request，只是把这个request放到队列里，然后接着从生成器里获取；
    4. 取尽第一部分的request，然后再获取第二部分的item，取到item了，就会放到对应的pipeline里处理；
    5. parse()方法作为回调函数(callback)赋值给了Request，指定parse()方法来处理这些请求 scrapy.Request(url, callback=self.parse)
    6. Request对象经过调度，执行生成 scrapy.http.response()的响应对象，并送回给parse()方法，直到调度器中没有Request（递归的思路）
    7. 取尽之后，parse()工作结束，引擎再根据队列和pipelines中的内容去执行相应的操作；
    8. 程序在取得各个页面的items前，会先处理完之前所有的request队列里的请求，然后再提取items。
    9. 这一切的一切，Scrapy引擎和调度器将负责到底。
    '''

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'news.163.com'
        if sel.xpath('//div[@class="post_time_source"]/text()'):
            time_ = sel.xpath('//div[@class="post_time_source"]/text()').extract_first().split()[0] + ' ' + sel.xpath('//div[@class="post_time_source"]/text()').extract_first().split()[1]
        else:
            time_ = 'unknown'
        date = '20' + pattern.group(2) + '/' + pattern.group(3)[0:2] + '/' + pattern.group(3)[2:]
        newsId = pattern.group(4)
        url = response.url
        title = sel.xpath("//h1/text()").extract()[0]
        contents = ListCombiner(sel.xpath('//p/text()').extract()[2:-3])
        comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{}'.format(newsId)
        # yield is a keyword that is used like return, except the function will return a generator.
        yield Request(comment_url, self.parse_comment, meta={'source':source,
                                                             'date':date,
                                                             'newsId':newsId,
                                                             'url':url,
                                                             'title':title,
                                                             'contents':contents,
                                                             'time':time_
                                                             })

    def parse_comment(self, response):
        result = json.loads(response.text)
        item = NewsItem()
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['url'] = response.meta['url']
        item['title'] = response.meta['title']
        item['contents'] = response.meta['contents']
        item['comments'] = result['cmtAgainst'] + result['cmtVote'] + result['rcount']
        item['time'] = response.meta['time']
        return item