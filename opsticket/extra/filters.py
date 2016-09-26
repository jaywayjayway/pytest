#coding:utf-8
from flask import redirect, url_for
from flask.ext.login import current_user
from datetime import datetime

def dateformat(s, formatter='%Y-%m-%d %H:%M:%S'):
    return datetime.strftime(s, formatter)

def AnonymousLogin():
    return redirect(url_for('auth.login'))

def unix_to_datetime(s):
    return str(datetime.fromtimestamp(int(s)))

if __name__ == '__main__':
    now = datetime.now()
    print dateformat(now)
