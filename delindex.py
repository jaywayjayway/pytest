#coding:utf-8
# 定时删除 30天以前的 ES 索引
# 索引格式为  access-Y-M-d  如 access-2017-03-12
#
import time
import requests

base_url='http://localhost:9200/'
log='/data/scripts/del.log'

def getindex(pattern='logstash-*'):
    '''
    default delte logstash index
    '''
    r = requests.get(base_url+pattern)
    index = {}
    for name in r.json().keys():
        index[name]=unix_time(name.split('-')[-1])
    return  index

def unix_time(datetime):
    return time.mktime(time.strptime(datetime,"%Y.%m.%d"))

def get_unixtime_before_30_days():
    return time.time() - 30 * 24 * 3600

def delindex(url):
    #print url
    requests.delete(url)
    open(log,"a+").write("Del Index  {0} \n".format(url))

#time.mktime(time.strptime('2017.01.01', "%Y.%m.%d"))
#print map(lambda x:time.mktime(time.strptime(x,"%Y.%m.%d")),getindex())

if __name__ == "__main__":
    template = '''
#######################################
{0}
#######################################
'''
    open(log,"a+").write(template.format(time.asctime( time.localtime(time.time()) )))
    base_time = get_unixtime_before_30_days()
    for k,v in  getindex("access-*").iteritems():
        if  v < base_time:
            delindex(url=base_url+k)

    for k,v in  getindex().iteritems():
        if  v < base_time:
            delindex(url=base_url+k)

