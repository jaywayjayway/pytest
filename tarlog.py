import time
import os
import shutil
import tarfile
from_unix=1477929600 ## unixstampe ## 
to_unix=1491926400
base_dir="/data/logs/example.com/logs/"

class  Copylog(object):
    """docstring for  Copylog"""
    def __init__(self,from_unix,to_unix ):
        super  (Copylog, self).__init__()
        self.from_unix = from_unix
        self.to_unix = to_unix



    def getdate(self):
        Date = []

        while self.from_unix <= self.to_unix:
             tmp = time.localtime(self.from_unix)
             y,m,d = str(tmp.tm_year),str(tmp.tm_mon),str(tmp.tm_mday)
             if len(m) == 1:
                m = "0"+m
             if len(d) == 1:
                d = "0"+d
             Date.append(y+m+d)
             self.from_unix += 86400
        return Date

    def ziplog(self):
        global base_dir
        dest_dir = "/tmp/regist_log"
        if  not  os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        Date = self.getdate()
        for name in Date:
            filename = "regist_"+name+".txt"
            try:
                shutil.copyfile(os.path.join(base_dir,filename), os.path.join(dest_dir,filename))
            except:
                pass

        tar = tarfile.open(dest_dir+".tgz","w:gz")
        for root,dir,files in os.walk(dest_dir):
            for file in files:
                fullpath = os.path.join(root,file)
                tar.add(fullpath)
        tar.close()

def execute(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return p.communicate()

def main():
    Log = Copylog(from_unix, to_unix)
    Log.ziplog()
if __name__ == '__main__':
    main()
