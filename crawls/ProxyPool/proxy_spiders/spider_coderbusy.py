import requests
import re
import logging
import time
import threading
from bs4 import BeautifulSoup

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}


def get_current_time():
    timenow = time.strftime('%Y-%m-%d %X', time.localtime())
    return timenow


def crawl():
    result = []
    for page in range(2):
        url = 'https://proxy.coderbusy.com/zh-cn/classical/anonymous-type/highanonymous/p%s.aspx' % (page + 1)
        try:
            html = requests.get(url, headers=headers, timeout=5).text
            table = BeautifulSoup(html, 'lxml').find('table', {'class': 'proxy-server-table'}).find_all('tr')
        except Exception as e:
            print('[%s][Spider][CoderBusy]Error:' % get_current_time(), e)
            continue
        for item in table[1:]:
            try:
                tds = item.find_all('td')
                ip = tds[0].get_text()
                port = tds[1].get_text()
            except:
                continue
            line = ip + ':' + port
            result.append(line.replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', ''))
    print('[%s][Spider][CoderBusy]OK!' % get_current_time(), 'Crawled IP Count:', len(result))
    return result


class SpiderCoderBusy(threading.Thread):
    def __init__(self):
        super(SpiderCoderBusy, self).__init__()

    def run(self):
        self.result = crawl()


if __name__=='__main__':
    crawl()
