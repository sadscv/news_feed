#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-12-18 下午4:25
# @Author  : sadscv
# @File    : IfengNews.py
import re

from scrapy import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule

from crawls.news_spider.items import NewsItem
from crawls.news_spider.spiders.newsSpiderUtils import ListCombiner



# 凤凰网  successful
class IfengNewsSpider(CrawlSpider):
    name = "ifeng_news_spider"
    allowed_domains = ['news.ifeng.com']
    start_urls = ['http://news.ifeng.com']

    # http: // book.ifeng.com / a / 20171115 / 108116_0.shtml
    #http: // fo.ifeng.com / a / 20171116 / 44763303_0.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.ifeng\.com)/a/(\d{8})/(\d+)\_0\.shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        date = pattern.group(2)[0:4] + '/' + pattern.group(2)[4:6] + '/' + pattern.group(2)[6:]
        if sel.xpath('//p[@class="p_time"]/span/text()'):
            time = sel.xpath('//p[@class="p_time"]/span/text()').extract()
        elif sel.xpath('//div[@class="yc_tit"]/p/span/text()'):
            time = sel.xpath('//div[@class="yc_tit"]/p/span/text()').extract()[0]
        elif sel.xpath('//div[@class="zuo_word fl"]/p/text()'):
            time = sel.xpath('//div[@class="zuo_word fl"]/p/text()').extract()[-1]
        else:
            time = "unknown"

        if sel.xpath('//h1[@id="artical_topic"]/text()'):
            title = sel.xpath('//h1[@id="artical_topic"]/text()').extract()
        elif sel.xpath('//div[@class="yc_tit"]/h1/text()'):
            title = sel.xpath('//div[@class="yc_tit"]/h1/text()').extract()
        elif sel.xpath('//div[@class="zhs_mid_02"]/h1/text()'):
            title = sel.xpath('//div[@class="zhs_mid_02"]/h1/text()').extract()
        else:
            title = "unknown"
        source = pattern.group(1)
        newsId = pattern.group(3)
        url = response.url
        if sel.xpath('//div[@id="main_content"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@id="main_content"]/p/text()').extract())
        elif sel.xpath('//div[@class="yc_con_txt"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="yc_con_txt"]/p/text()').extract())
        elif sel.xpath('//div[@class="yaow"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="yaow"]/p/text()').extract())
        else:
            contents = "unknown"
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

