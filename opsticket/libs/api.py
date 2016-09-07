#coding:utf-8
import json
import urllib2

from opsticket import config
from opsticket import redis_store

def http_get(url='', method='get', headers=None, **kw):
    req = urllib2.Request(url)
    req.get_method=lambda: method.upper()
    resp = urllib2.urlopen(req)
    try:
        data = json.loads(resp.read())
    except:
        return None
    return data

def plat_list():
    data = redis_store.get(config.PLAT_KEY)
    if not data:
        data = http_get('%s/game/openplat' % config.GAME_URL)
        if data:
            redis_store.set(config.PLAT_KEY, json.dumps(data))
    else:
        data = json.loads(data)
    return data["plats"]

def game_list(g):
    data = http_get('%s/api/platset?platid=%s' % (config.GAME_URL, g.plat_id))
    if data["success"]:
        return data["msg"]
    return []

def zone_list(g, gameid):
    data = http_get('%s/api/zones?gameid=%s&platid=%s' % (config.GAME_URL, gameid, g.plat_id))
    if data["success"]:
        return data["msg"]
    return []


if __name__ == '__main__':
    print plat_list()
