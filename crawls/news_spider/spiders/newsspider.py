#!usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author: Jeff Zhang
@date:   2017-08-23
"""

from crawls.news_spider.items import NewsItem

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
import json
import re
from scrapy import Request
import time

def ListCombiner(lst):
    string = ""
    for e in lst:
        string += e
    return string.replace(' ','').replace('\n','').replace('\t','')\
        .replace('\xa0','').replace('\u3000','').replace('\r','')


class NeteaseNewsSpider(CrawlSpider):
    website_possible_httpstatus_list = [404, 403, 301]
    name = "netease_news_spider"
    start_urls = ['http://news.163.com/']
    # Spider中间件会对Spider发出的request进行检查，只有满足allow_domain才会被允许发出
    allowed_domains = ['news.163.com']


    # http://news.163.com/17/0823/20/CSI5PH3Q000189FH.html
    # Todo fix bug
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

            yield Request(comment_url, self.parse_comment, meta={'source':source,
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


class TencentNewsSpider(CrawlSpider):
    name = 'tencent_news_spider'
    # allowed_domains = ['news.qq.com']
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
                yield Request(comment_url, self.parse_comment, meta={'source': source,
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
                return item

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

#wirted by myself 搜狐ｏｋ
class SohuNewsSpider(CrawlSpider):
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
        item['source'] = source
        item['time'] = time
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['comments'] = comments
        yield item


# 江西晨报  有问题
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
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item

#新气象  successful
class ZgqxbNewsSpider(CrawlSpider):
    name = "zgqxb_news_spider"
    allowed_domains = ['zgqxb.com.cn']
    start_urls = ['http://www.zgqxb.cn']
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
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item


#新民网   successful
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
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item


# 央视新闻 successful
class CctvNewsSpider(CrawlSpider):
    name = "cctv_news_spider"
    allowed_domains = ['news.cctv.com']
    start_urls = ['http://news.cctv.com']
    #http: // jiankang.cctv.com / 2017 / 11 / 17 / ARTIsSTfqrpnb6Nj2UZydIXo171117.shtml
    #http: // tv.cctv.com / 2017 / 11 / 19 / VIDELf9eHnwFxj0h0p77qwNV171119.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.cctv\.com)/(\d{4})/(\d{2})/(\d{2})/(\w+)\.shtml'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
        ]
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2) + '/' + pattern.group(3) + '/'+ pattern.group(4)
        newsId = pattern.group(5)
        if sel.xpath('//span[@class="info"]/i/text()'):
            time = sel.xpath('//span[@class="info"]/i/text()').extract()
        elif sel.xpath('//span[@class="time"]/text()'):
            time = sel.xpath('//span[@class="time"]/text()').extract()
        else:
            time = "unknown"
        if sel.xpath('//div[@class="cnt_bd"]/h1/text()'):
            title = sel.xpath('//div[@class="cnt_bd"]/h1/text()').extract()
        elif sel.xpath('//h3[@class="title"]/text()'):
            title = sel.xpath('//h3[@class="title"]/text()').extract()
        else:
            title = "unknown"
        url = response.url
        contents = ListCombiner(sel.xpath('//div[@class="cnt_bd"]/p/text()').extract())
        comments = 0

        item = NewsItem()
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item





# 江南都市报 successful
class JndsbNewsSpider(CrawlSpider):
    name = "jndsb_news_spider"
    allowed_domains = ['jndsb.jxnews.com.cn']
    start_urls = ['http://jndsb.jxnews.com.cn']
    #http://jndsb.jxnews.com.cn/system/2017/06/17/016210714.shtml
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
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item




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
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item

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
        item['source'] = source
        item['time'] = time
        item['date'] = date
        item['title'] = title
        item['contents'] = contents
        item['newsId'] = newsId
        item['url'] = url
        item['comments'] = comments
        yield item


