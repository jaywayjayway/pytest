#coding:utf-8
import urllib
import urllib2
import json
from haproxystats import HAProxyServer
import time

def alert(content=''):
    url='http://notify.example.com:1122/forward'
    values = {"reciver": ["shenzhiwei@example.com","tangchangfu@example.com"],"content":content}
    data = json.dumps(values)             # 对数据进行JSON格式化编码
    req = urllib2.Request(url, data)       # 生成页面请求的完整数据
    response = urllib2.urlopen(req)       # 发送页面请求
    print content
    return True

def monitor():
    haproxy = HAProxyServer('127.0.0.1:1088/admin?admin','admin','admin')
    backlist = {}
    for idx,bend in enumerate(haproxy.backends):
        backlist.setdefault(bend.name,idx)
    server = {}
    for b  in  haproxy.backends:
        #print b.name,b.status,b.listeners
        #print b.name,b.status,svr.name,svr.status
        for svr in b.listeners:
            if b.status != "UP" or  svr.status != "UP":
                content = '域名 %s 下面的主机  %s 出现故障，请速查看' %(b.name.encode('ascii'),svr.name.encode('ascii'))
                Time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                file('/tmp/monitor.log','a+').write(Time+":   "+content+'\n')
                alert(content)
    return


if __name__ == '__main__':
    while True:
        monitor()
        time.sleep(10)