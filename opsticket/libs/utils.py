#coding:utf-8
import re
import time
import json
import uuid
import random
import datetime
import hashlib

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:    
            return json.JSONEncoder.default(self, obj)

def get_uuid():
    return "%s" % uuid.uuid1(node=random.randint(1, 999999999999))

def NOW():
    return datetime.datetime.now()

def today_zone():
    t = datetime.datetime.now().strftime('%Y-%m-%d')
    return [datetime.datetime.strptime('%s 00:00:01' % t, '%Y-%m-%d %H:%M:%S'), \
            datetime.datetime.strptime('%s 11:59:59' % t, '%Y-%m-%d %H:%M:%S')]

def now_unix():
    return int(time.time())

def tomrrow_work_unix():
    limit_at = datetime.datetime.now().today() + datetime.timedelta(days=1)
    #tomorrow = datetime.datetime.now().today() + datetime.timedelta(days=1)
    #tomorrow_work = '%s 09:00:00' % tomorrow.strftime('%Y-%m-%d')
    #limit_at = datetime.datetime.strptime(tomorrow_work, '%Y-%m-%d %H:%M:%S')
    return int(time.mktime(limit_at.timetuple()))

def encryption(string):
    return hashlib.md5('YB$a,3'+string+'$$%@cds').hexdigest()

def complexity_check(string):
    if len(string) < 8:
        return None
    if not re.search(r'[A-Z]', string):
        return None
    if not re.search(r'[a-z]', string):
        return None
    if not re.search(r'[0-9]', string):
        return None
    return True
