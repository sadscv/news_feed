## ProxyPool

### 1.配置
#### 数据库配置
在`conf.py`中修改数据库配置，并新建`proxypool`表。
```
sql>create table proxypool(ip char(20),port char(5),time char(30));
```

#### 安装Python库
```
pip3 install pymysql
pip3 install requests
pip3 install bs4
pip3 install lxml
```
### 2.运行
抓取代理IP
```
python3 proxypool.py
```

定时验证IP
```
python3 verify.py
```

### 3.启用HTTP Server
感谢 <a href="https://github.com/luzzbob">Luzz</a>

```
python3 server.py
curl http://localhost:5000/
```





