#coding:utf-8
import json
import urllib2

from opsticket import config
from opsticket import redis_store

def http_get(url='', method='get', headers={}, data=None):
    if data:
        data = json.dumps(data)
        method='post'
    req = urllib2.Request(url, data, headers=headers)
    print "%s %s " % (method, url)
    req.get_method=lambda: method.upper()
    try:
        resp = urllib2.urlopen(req)
        data = json.loads(resp.read())
    except Exception,e:
        return None
    return data

def plat_list():
    data = redis_store.get(config.PLAT_LIST)
    if not data:
        data = http_get('%s/game/openplat' % config.GAME_URL)
        if data:
            redis_store.set(config.PLAT_LIST, json.dumps(data))
    else:
        data = json.loads(data)
    return data["plats"]

def plat_info(plat_id):
    data = redis_store.get(config.PLAT_KEY % locals())
    if not data:
        data = http_get('%s/api/platinfo?platid=%s' % (config.GAME_URL, plat_id))
        if data and data["success"]:
            redis_store.set(config.PLAT_KEY % locals(), json.dumps(data))
    else:
        data = json.loads(data)
    return data["msg"]

def game_list(g):
    data = http_get('%s/api/platset?platid=%s' % (config.GAME_URL, g.plat_id))
    if data and data["success"]:
        return data["msg"]
    return []

def open_game(g):
    print g.token
    data = http_get('%s/api/gameset' % config.GAME_URL, headers={"X-Auth-Token":g.token})
    if data and data["success"]:
        return data["msg"]
    return []

def profile_game(g, gameid=None):
    data = open_game(g)
    exists = [int(i.split(":")[-1]) for i in redis_store.keys("GAME:SETTING:*")]
    for i in data:
        if gameid and i["gameid"] == int(gameid):
            continue
        if i["gameid"] in exists:
            data.remove(i)
    return data

def group_list(g, gameid):
    print g.token
    data = http_get('%s/api/gamegroup?gameid=%s' % (config.GAME_URL, gameid), headers={"X-Auth-Token":g.token})
    if data and data["success"]:
        return data["msg"]
    return []

def zone_list(g, gameid):
    data = http_get('%s/api/zones?gameid=%s&platid=%s' % (config.GAME_URL, gameid, g.plat_id))
    if data and data["success"]:
        return data["msg"]
    return []

def zone_limit(g, gameid):
    data = http_get('%s/api/zonelimit?gameid=%s&platid=%s' % (config.GAME_URL, gameid, g.plat_id))
    if data and data["success"]:
        return data["msg"]
    return 0

def cmdid(g ,gameid, category):
    data = redis_store.get(config.CMD_KEY % locals())
    if not data:
        data = http_get('%s/game/execcmd?gameid=%s' % (config.GAME_URL, gameid), headers={"X-Auth-Token":g.token})
        if data:
            for c in data["cmds"]:
                if c["cmdtype"] == category:
                    redis_store.set(config.CMD_KEY % locals(), c["id"], ex=60*60*2)
                    return c["id"]
    else:
        return data
    return None

def send_cmd(g, cmdid, ticket, ext=None):
    data = {"gameid":gameid,"cmdid":cmdid, "platid":ticket.plat_id, \
            "title": u"%s-%s-运营工单" % (ticket.appname, ticket.platname)}
    if ext and isinstance(ext, dict):
        data.update(ext)
    print "post /game/opsmanage data=%s" % data
    return True
    #data = http_get('%s/game/opmanage' % config.GAME_URL, method='post', headers={"X-Auth-Token":g.token}, data=data)
    if data and data["result"]["status"] == 5:
        return True
    return False

def host_scheduler(g, gameid, ticket):
    data = {"gameid":gameid,"platid":ticket.plat_id,"sids":[i.target for i in ticket.ticketsub.filter_by(allow=None).all()]}
    game_setting = redis_store.get(config.GAME_SETTING % data)
    if game_setting:
        try:
            _set = json.loads(game_setting)
        except:
            return None
    else:
        return None
    data.update(_set)
    data = http_get('%s/api/scheduler' % config.GAME_URL, headers={"X-Auth-Token":g.token}, data=data)
    if data and data["success"]:
        return data["msg"]
    return None

if __name__ == '__main__':
    print plat_list()
