# -*- coding:utf-8 -*-
import os
import sys
import datetime
import shutil
from signal import SIGUSR1

NgxSign="/usr/local/openresty/nginx/run/nginx.pid"
DestBaseDir="/data/logs/cutlog/"
LogDir=["/data/logs/weblog/","/tmp/weblog/"]

class CutLog():
    def __init__(self,pattern):
        self.s = pattern
        self.year = None
        self.month = None
        self.day = None

    def search(self):
        global LogDir
        dirList = LogDir
        retList = []
        while len(dirList):
            dir = dirList.pop()
            itemList = os.listdir(dir)

            for item in itemList:
                item = os.path.join(dir, item) #拼接子项绝对路径
                if os.path.isdir(item):
                    dirList.append(item)
                    continue
                for pattern in self.s:
                    if item.find(pattern) != -1:
                        retList.append(item)
                        continue
                        # map(lambda x: if  retList.append(x),[ p  for p  in self.s if item.find(p) != -1])
                        #elif item.find(self.s) != -1:
                        #retList.append(item)
        return retList

    @property
    def now_time(self):
        now = datetime.datetime.now()
        # 取前一小时 ##
        d1 = now - datetime.timedelta(days=1)
        self.year=d1.year
        self.month=d1.month
        self.day=d1.day
        return  d1.strftime("%Y_%m_%d_%H")

    def Move(self,files=[],timestamp=''):

        global DestBaseDir
        DestDir=os.path.join(DestBaseDir,str(self.year)+str(self.month)+str(self.day))
        if not os.path.exists(DestDir):
            os.mkdir(DestDir)
        for item in files:
            if os.stat(item).st_size == 0:
                continue
            filename = os.path.basename(item)
            if item.find("/tmp") == 0:
                os.remove(item)
                continue
            #dest_file = base_file+"_"+timestamp
            if not os.path.exists(os.path.join(DestDir,filename)):
                shutil.move(item,os.path.join(DestDir,filename))

        pid=file(NgxSign,"r").read()
        os.kill(int(pid),SIGUSR1)

if __name__ == '__main__':
    log=CutLog(["access","error"])
    files=log.search()
    timestamp=log.now_time
    log.Move(files,timestamp)
    #os.system("find %s -maxdepth 2 -mtime +7 -exec rm {} \;"% (DestBaseDir))

