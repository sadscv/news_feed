#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:19
# @Author  : zjms
# @File    : SohuNews.py
import json
import re

from scrapy import Request
from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



#wirted by myself 搜狐ｏｋ
class SohuNewsSpider(CrawlSpider):
    website_possible_httpstatus_list = [404, 302]
    name = "sohu_news_spider"
    start_urls = ['http://news.sohu.com/',
                  'http://travel.sohu.com/',
                  'http://it.sohu.com/',
                  'http://sports.sohu.com/',
                  'http://yule.sohu.com/',
                  'http://cul.sohu.com/',
                  'http://society.sohu.com/'
                  ]


    allowed_domains = ['sohu.com']
    # http://www.sohu.com/a/203596129_100001551?_f=index_chan08news_5
    # url_pattern = r'http://www.sohu.com/a/(\d{9})\_(\d{6, 9})\?\_f=index\_chan08(\w+)\_(\d{1,4})'
    url_pattern = r'www.sohu.com/a/(\d{6,9})\_(\d{6,9})'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        title = sel.xpath('//div[@class="text-title"]/h1/text()').extract()[0].split()
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'news.sohu.com'

        date = sel.xpath('//div[@class="article-info"]/span/text()').extract()[0][0:10]
        time = sel.xpath('//div[@class="article-info"]/span/text()').extract()[0][10:-1]
        url = response.url
        newsId = re.findall(r'www.sohu.com/a/(.*?)?_',url, re.S)[0]
        contents = ListCombiner(sel.xpath('//article[@class="article"]/p/text()').extract())
        # comments= sel.xpath('//div[@class="right"]/span'

        comments = 0
        item = NewsItem()
        item['source'] = self.name
        item['time'] = time
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['comments'] = comments
        yield item
