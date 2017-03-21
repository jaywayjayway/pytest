#-*- coding:utf-8 -*-
import redis
import cPickle
from alert.utils import UserConfig


'''
config.json example:
{

  "cache": "redis://127.0.0.1:/6379/0",

}
'''

class UserConfig(dict):
    """ loads the json configuration file """
    def _string_decode_hook(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            rv[key] = value
        return rv

    def __init__(self):
        dict.__init__(self)
        configfile = join(dirname(realpath(__file__)), 'config.json')
        self.update(json.load(open(configfile), object_hook=self._string_decode_hook))


options = UserConfig()
class Backend(object):
    def __init__(self):
        cached_backend = options['cache']
        _conn = cached_backend.split("//")[1]
        if '@' in _conn:
            passwd, host_port = _conn.split('@')
        else:
            passwd = None
            host_port = _conn
        if passwd:
            passwd = passwd
        host, db_p = host_port.split(':')
        tmp,port, db = db_p.split('/')
        self.conn = redis.StrictRedis(host=host, port=port, db=db, password=passwd)
    def get(self, id, default=None):
        """
        Return object with id
        """
        try:
            ret = self.conn.get(id)
            if ret:
                ret = cPickle.loads(ret)["msg"]
        except:
            ret = default
        return ret

    def set(self, id, user_msg, timeout=options['cache_time']):
        """
        Set obj into redis-server.
        Expire 3600 sec
        """
        try:
            if user_msg:
                msg = cPickle.dumps({"msg": user_msg})
                self.conn.set(id, msg)
                self.conn.expire(id, timeout)
                return True
        except:
            self.conn.delete(id)
            return False

    def delete(self, id):
        try:
            self.conn.delete(id)
        except:
            pass

    def get_user_roles(self, id):
        cache_id = '%s_%s' % ('roles', id)
        if not self.get(id):
            return []
        roles = self.get(cache_id)
        if not roles:
            if 'roles' in self.get(id):
                roles = [role['name'] for role in self.get(id)['roles']]
                self.set(cache_id, roles)
        return roles

    def keys(self, key):
        return self.conn.keys(key)