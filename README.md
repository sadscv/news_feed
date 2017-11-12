# 公告栏

### 学习资料-Git 

[官方文档](https://git-scm.com/book/zh/v2)  强烈推荐  

 此外
[廖雪峰的Git教程](https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000)

书籍推荐：
Python爬虫开发与项目实战 [pdf下载 密码:7fyj](https://pan.baidu.com/s/1hrLr7yk)

[实体书购买地址](https://item.jd.com/12206762.html#none)

(To be update)

---
### 注意事项

### 在服务器上使用
1. 切换用户 & su test (username:test password:test)
2. 进入目录 & cd /home/test/Repositories/news_feed
3. 切换conda环境 & source activate crawl
* 配置文件 config.py 出于安全考虑未加入版本控制，若需更改请SSH至服务器手动编辑。
* mysql 连接密码参见配置文件，请勿滥用，如需修改数据库结构请咨询 @sadscv


# 项目介绍
简介：
此项目可监控近千家中国企业的官方网站的新闻动态，如有更新，系统能在最短2分钟之内通过邮件发送更新的标题和链接。
更新的信息流也可通过浏览器查看。监控的公司和站点可以添加删除。

原理：
定期抓取网站html, 使用difflib比对新旧页面源码，发现增加的部分，提取url和text，过滤筛选，保存MySQL数据库。
定期把更新的url和text，通过邮件发送给订阅者。




#### 环境准备
系统需安装MySQL和Redis数据库以及Python3.
建议安装Python3虚拟环境之后运行。

安装依赖包
```
pip install -r requirements.txt
```




#### Web运行
创建MySQL数据库

连接MySQL，执行
```
mysql> create database news_feed default charset utf8;
```

创建表
```
python models.py
```

运行
```
python app.py
```
浏览器打开
http://127.0.0.1:8888/

![news feed](http://oiip5z89k.bkt.clouddn.com/WechatIMG8.jpeg)


1. 用户

* 新用户注册
仅用于管理员注册的一个接口
http://127.0.0.1:8888/register

* 用户订阅
订阅用户能定期收到邮件推送
http://127.0.0.1:8888/subscription
![subscription](http://oiip5z89k.bkt.clouddn.com/WechatIMG2.jpeg)


2. 公司、站点管理

在公司栏可以查看公司列表和添加公司，点击公司进入公司Profile页可以编辑

导入收集的公司信息
```
cd utils/ ; python xlsx_reader.py
```

![company list](http://oiip5z89k.bkt.clouddn.com/WechatIMG7.jpeg)
![company profile](http://oiip5z89k.bkt.clouddn.com/WechatIMG9.jpeg)


3. 抓取日志
http://127.0.0.1:8888/log
![crawler log](http://oiip5z89k.bkt.clouddn.com/WechatIMG6.jpeg)


4. 信息流

资讯栏包括全部信息，海外栏是包含关键词的企业出海信息

可以在关键词栏管理关键词。

将国家和地区名导入数据库
```
cd utils/ ; python keywords_reader.py
```




#### 抓取控制
1. 开启celery任务队列(需要先安装redis)

在系统根目录执行
```
celery -A info_engine worker -c 20 -l info
```

2. 运行爬虫

```
python info_engine.py
```

抓取频率, Celery参数可在config.py文件设置



#### 发送邮件
需要在config设置EMAIL和SEND_MAIL_INTERVAL参数

启动定时发邮件程序
```
python mail_bot.py
```

手动发邮件可以执行：
```
cd utils/ ; python send_email.py
```







