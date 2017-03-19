##### Base #####
SECRET_KEY='12ASF$$VH2'
SESSION_COOKIE_NAME='OP-TICKET'

##### DB ####
SQLALCHEMY_DATABASE_URI='sqlite:////tmp/test.db'
SQLALCHEMY_TRACK_MODIFICATIONS=True

##### Cache ####
USER_KEY='USERS:%(user_id)s'
Keystone_url='http://console.lightcloud.cn:5000/v2.0'

##### Extra ###
PLAT_LIST='PLAT:list'
PLAT_KEY='PLAT:%(plat_id)s'

GAME_URL='http://game.opstack.cc:8334'
GAME_INFO='GAME:INFO:%(gameid)s'
GAME_SETTING='GAME:SETTING:%(gameid)s'
GAME_MAXZONE='GAME:MAX_ZONE:%(gameid)s:%(platid)s'
CMD_KEY='CMD:%(category)s:%(gameid)s'

SCHEDULER_ID='scheduler_%(uuid)s'

HOOK='http://'
SCHEDULER_LOCK='LOCK:SCHEDULER'
