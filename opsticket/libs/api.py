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
    print "%s %s %s" % (method, url, data)
    req.get_method=lambda: method.upper()
    try:
        resp = urllib2.urlopen(req)
        data = resp.read()
        print data
        data = json.loads(data)
    except Exception,e:
        print e
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
        for i in data["msg"]:
            i["appname"] = i["cnname"]
            redis_store.set(config.GAME_INFO % i, json.dumps(i))
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
    data = http_get('%s/api/gamegroup?gameid=%s' % (config.GAME_URL, gameid), headers={"X-Auth-Token":g.token})
    if data and data["success"]:
        return data["msg"]
    return []

def zone_list(g, gameid):
    data = http_get('%s/api/zones?gameid=%s&platid=%s' % (config.GAME_URL, gameid, g.plat_id))
    if data and data["success"]:
        return [i for i in data["msg"] if i["sid"] < 9900]
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
    data = {"gameid":ticket.app_id,"cmdid":cmdid, "platid":ticket.plat_id, \
            "title": u"%s-%s-运营工单" % (ticket.appname, ticket.platname), "wechat_call":True}
    if ext and isinstance(ext, dict):
        data.update(ext)
    data = http_get('%s/game/opmanage' % config.GAME_URL, method='post', headers={"X-Auth-Token":g.token}, data=data)
    if data and data["result"]["status"] == 5:
        return True
    return False

def host_scheduler(g, gameid, ticket):
    if hasattr(ticket, 'ticketsub'):
        data = {"gameid":gameid,"platid":ticket.plat_id,"sids":[i.target for i in ticket.ticketsub.filter_by(allow=None).all()]}
    else:
        data = {"gameid":gameid,"platid":ticket.ticket.plat_id,"sids":[ticket.target]}
    print "Scheduler:",data
    game_setting = redis_store.get(config.GAME_SETTING % data)
    if game_setting:
        try:
            _set = json.loads(game_setting)
        except:
            return None
    else:
        return 2333
    #lock = redis_store.get(config.SCHEDULER_LOCK)
    #if lock:
    #    try:
    #        lock = json.loads(lock)
    #    except:
    #        lock = []
    #    if lock:
    #        print "Current Time should ignore hosts %s" % lock
    #        data.update({"ignore_hosts": ",".join(lock)})
    data.update(_set)
    data = http_get('%s/api/scheduler' % config.GAME_URL, headers={"X-Auth-Token":g.token}, data=data)
    if data and data["success"]:
        return data["msg"]
    return None

def setting_list():
    data = []
    for key in redis_store.keys(config.GAME_SETTING % {"gameid": "*"}):
        p = json.loads(redis_store.get(key))
        data.append(p)
    return data

if __name__ == '__main__':
    print setting_list()
