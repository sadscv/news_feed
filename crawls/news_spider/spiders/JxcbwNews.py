#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:20
# @Author  : sadscv
# @File    : JxcbwNews.py
# 江西晨报  有问题
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



class JxcbwNewsSpider(CrawlSpider):
    name = "jxcbw_news_spider"
    allowed_domains = ['jxcbw.cn']
    start_urls = ['http://www.jxcbw.cn/mainpages/default.aspx']
    #http://www.jxcbw.cn/mainpages/NewsInfo.aspx?NewsID=69366&NewsType=LE123
    #http://www.jxcbw.cn/mainpages/NewsInfo.aspx?NewsID=70152&NewsType=LE107
    url_pattern = r'http://www.jxcbw.cn/[a-z]+/NewsInfo.aspx?(NewsID=\d{3,8}&NewsType=LE\d{1,7})'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
         ]
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'www.jxcbw.cn'
        time = sel.xpath('//span[@class="time fl"]/text()').extract()
        date = time[0]
        title = sel.xpath('//h2[@class="title-class2"]/text()').extract()
        newsId = pattern.group(1)
        url = response.url
        # if sel.xpath('//div[@id="content"]/div/text()'):
        #     contents = ListCombiner(sel.xpath('//div[@id="content"]/div/text()').extract())
        # else:
        #     contents = "unknown"
        comments= 0
        contents = 0

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