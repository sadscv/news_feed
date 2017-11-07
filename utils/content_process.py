# --*-- coding: utf-8 --*--

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)

from urllib.parse import urlparse
from utils.blacklist import blacklist_url, blacklist_text


def complement_url(url, site):
    """
    通过匹配给定的url以及当前site,对某些奇怪的url做一些拼接处理,使得其能符合正常规则
    e.g.
    url : ./foo.html/bar?id=1&result=0
    site : https://www.demo.com/
    complement_url: https://www.demo.com/foo.html/bar?id=1&result=0

    :param url: <string>
    :param site: <string>
    :return: <string>
    """
    if not url.startswith("http"):
        base_url = urlparse(site).scheme + "://" + urlparse(site).netloc
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




def check_content(url, text):
    """
    check if given 'url' is exactly match url regulation and 'text' similar to news title.
    如 <a href="url">标签中 url是否为规范地址。
    <a>text</a> 中的text是否是长度合规的字符串。

    :param url:<string>
    :param text: <string>
    :return: <Boolean>
    """
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