#coding:utf-8
import json
import pickle
import urllib2
import datetime
from opsticket import config
from opsticket import redis_store

class KeystoneUser(object):
    def __init__(self, user_info):
        self.user_info = user_info
        self.username = user_info["access"]["user"]["username"]
        self.user_id = user_info["access"]["user"]["id"]
        self.email = None
        self.account = user_info["access"]["user"]["name"]
        self.role = 2

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

    @property
    def expires(self):
        return token_timeout(self.user_info)

def authentication(username, password):
    headers = {'Content-type': 'application/json'}
    data = {
        "auth":
            {"passwordCredentials":
                {
                    "username":username,
                     "password":password,
                 }
            }
        }
    req = urllib2.Request(config.Keystone_url+'/tokens', json.dumps(data), headers=headers)
    try:
        resp = urllib2.urlopen(req)
    except Exception,e:
        print e
        return None
    token_info = json.loads(resp.read())
    user = KeystoneUser(token_info)
    redis_store.set(config.USER_KEY % {"user_id":user.user_id}, pickle.dumps({"user":user}), ex=user.expires)
    return user

def token_timeout(token):
    token_expires = token.get("access", {}).get("token", {}).get("expires", None)
    if token_expires:
        token_expires = datetime.datetime.strptime(token_expires, '%Y-%m-%dT%H:%M:%SZ')
        utcnow = datetime.datetime.utcnow()
        if token_expires > utcnow:
            return (token_expires - datetime.datetime.utcnow()).seconds - 60
    return 1


if __name__ == '__main__':
    print authentication('test', 'test').get_id()
