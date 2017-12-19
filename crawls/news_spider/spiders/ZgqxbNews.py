#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:24
# @Author  : sadscv
# @File    : ZgqxbNews.py
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner


#新气象  successful
class ZgqxbNewsSpider(CrawlSpider):
    name = "zgqxb_news_spider"
    allowed_domains = ['zgqxb.com.cn']
    website_possible_httpstatus_list = [404, 403, 301, 302]
    start_urls = ['http://www.zgqxb.com.cn']
    # http: // www.zgqxb.com.cn / pressman / bjdp / 201711 / t20171102_66412.htm
    # http: // www.zgqxb.com.cn / kjzg / kejidt / 201711 / t20171121_66600.htm
    url_pattern = r'(http://www\.zgqxb\.com\.cn)/.*/\d{6}/t(\d+)_(\d+).htm'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
        ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] +'/' + date[6:]
        newsId = pattern.group(3)
        #时间
        if sel.xpath('//span[@class ="l01 gray"]/text()'):
            time = sel.xpath('//span[@class ="l01 gray"]/text()').extract()[-1]
        else:
            time = "unknown"
        #标题
        if sel.xpath('//strong/b/text()'):
            title = ListCombiner(sel.xpath('//strong/b/text()').extract())
        else:
            title = "unknown"
        url = response.url
        #内容
        if sel.xpath('//div[@class="TRS_Editor"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="TRS_Editor"]/p/text()').extract())
        elif sel.xpath('//font[@class="font_txt_zw"]/p/text()'):
            contents = ListCombiner(sel.xpath('//font[@class="font_txt_zw"]/p/text()').extract())
        elif sel.xpath('//font[@class="font_txt_zw"]/text()'):
            contents = ListCombiner(sel.xpath('//font[@class="font_txt_zw"]/text()').extract())
        else:
            contents = 'unknown'
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


