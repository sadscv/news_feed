import threading
import time

import logging
import pymysql
import requests
from celery import Celery

from crawls.ProxyPool.proxy_spiders.spider_66ip import SpiderIP66
from crawls.ProxyPool.proxy_spiders.spider_89ip import SpiderIP89
from crawls.ProxyPool.proxy_spiders.spider_coderbusy import SpiderCoderBusy
from crawls.ProxyPool.proxy_spiders.spider_data5u import SpiderData5u
from crawls.ProxyPool.proxy_spiders.spider_ip181 import SpiderIP181
from crawls.ProxyPool.proxy_spiders.spider_kxdaili import SpiderKxdaili
from crawls.ProxyPool.proxy_spiders.spider_mimvp import SpiderMimvp
from crawls.ProxyPool.proxy_spiders.spider_xicidaili import SpiderXicidaili

from CONFIG.config import DB


# all class of crawler

celery_app = Celery('crawls.ProxyPool.proxypool')
celery_app.config_from_object('CONFIG.celeryconfig')
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

logger = logging.getLogger(__name__)
CRAWLERS = [SpiderMimvp, SpiderCoderBusy, SpiderIP66, SpiderIP89,
            SpiderKxdaili, SpiderData5u, SpiderIP181,
            SpiderXicidaili]

class IsEnable(threading.Thread):
    def __init__(self, queue,result, debug=False):
        super(IsEnable, self).__init__()
        self.debug = debug
        self.tag = False
        self.q = queue
        self.results = result
        # if debug:
        #     self.proxies = {
        #         'http': '%s'%ip
        #     }
        # else:
        #     self.proxies = {
        #         'http': 'http://%s' % ip
        #     }

    def run(self):
        while not self.q.empty():
            self.work = self.q.get()
            self.ip = self.work[1]
            if self.debug:
                self.proxies = {'http': '%s'%self.ip}
            else:
                self.proxies = {'http': 'http://%s' % self.ip}
            try:
                html = requests.get('http://httpbin.org/ip',
                                    proxies=self.proxies, timeout=5).text
                result = eval(html)['origin']
                # if len(result.split(',')) == 2:
                #     return
                if result in self.ip:
                    self.results[self.work[0]] = self.ip
                    # with lock:
                    #     self.insert_into_sql()
            except:
                return
            self.q.task_done()

    def get_result(self):
        if self.tag:
            return self.tag
        else:
            return False

    def insert_into_sql(self):
        global cursor
        global conn
        global CRAWL_IP_COUNT
        if self.debug:
            print('[IsEnable][Debug][valid ip:%s]', self.ip)
            self.tag = self.ip
        else:
            try:
                date = time.strftime('%Y-%m-%d %X', time.localtime())
                print("insert into proxypool(ip,port,time) values" + str(
                    (self.ip.split(':')[0], self.ip.split(':')[1], date)))
                cursor.execute("insert into proxypool(ip,port,time) values " + str(
                    (self.ip.split(':')[0], self.ip.split(':')[1], date)))
                print('execute')
                conn.commit()
                CRAWL_IP_COUNT += 1
            except:
                pass


def get_current_time():
    return time.strftime('%Y-%m-%d %X', time.localtime())



@celery_app.task
def update_proxy():
    global CRAWL_IP_COUNT
    global cursor

    CRAWL_IP_COUNT = 0
    conn = pymysql.connect(host=DB['HOST'],
                        user=DB['USER'],
                        passwd=DB['PASSWORD'],
                        db=DB['DB_NAME'],
                        port=DB['PORT'],
                        charset='utf8')
    cursor = conn.cursor()
    result = []
    tasks = []
    for crawler in CRAWLERS:
        task = crawler()
        task.setDaemon(True)
        task.start()
        task.join()
        tasks.append(task)
    for task in tasks:
        try:
            result += task.result
        except:
            continue
    print('length of result:{}'.format(len(result)))

    while (len(result)):
        num = 0
        # 循环测试IP,开50个线程
        while (num < 500):
            try:
                ip = result.pop()
                print('[Spider][ProxyPool][Testing ip:[%s]'%ip)
            except:
                break
            work = IsEnable(ip=ip, debug=False)
            work.setDaemon(True)
            work.start()
            num += 1
        time.sleep(5)
    try:
        conn.commit()
    except:
        pass
    cursor.close()
    conn.close()
    print('[%s][ProxyPool]Crawl IP Count:' %
          get_current_time(), CRAWL_IP_COUNT)
    print('[%s][ProxyPool][Sleeping]' % get_current_time())


if __name__ == '__main__':
    CRAWL_IP_COUNT = 0
    lock = threading.Lock()

    # update_proxy.delay()
    update_proxy()

        # TOdo 明天要做的事，调用celery接口，随时更新代理ＩＰ，继续调试．

