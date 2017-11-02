import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)

from urllib.parse import urlparse
from utils.blacklist import blacklist_url, blacklist_text


def complement_url(url, site):  #组合完整的url地址
    if not url.startswith("http"):
        #使用urlparse模块可以对url进行分析，最主要的操作就是拆分和合并url的各个部件
        base_url = urlparse(site).scheme + "://" + urlparse(site).netloc  #parsed.scheme 网络协议 ,parsed.netloc服务器位置,也可能有用户信息
        if url.startswith("./"):
            new_url = site.rstrip('/') + url[1:]
            return new_url

        if url.startswith("../..") or url.startswith("../"):
            url = url.lstrip("../")
            new_url = base_url + "/" + url
            return new_url

        if url.startswith("//www"):
            new_url = urlparse(site).scheme + ":" + url
            return new_url

        if url.startswith("//") and not url.startswith("//www"):
            new_url = base_url + url[1:]
            return new_url

        if url.startswith("/") and not url.startswith("//"):
            new_url = base_url + url
            return new_url

        if url.startswith("?"):
            new_url = base_url + urlparse(site).path + url
            return new_url
    else:
        return url




def check_content(url, text):  #将url,text和黑名单对比
    if (not url) or (not text):
        return False

    if url.startswith("javascript"):
        return False

    if url in blacklist_url or text.strip() in blacklist_text:
        return False

    if text.isdigit():
        return False

    if len(text.strip()) <= 10 or len(text.strip()) > 50:
        return False


    return True



if __name__ == "__main__":
    u = "./zhhy/201709/t20170919_13784.html"
    s = "http://www.jinnengjt.com/xwzx/"
    complement_url(u, s)