##### Base #####
SECRET_KEY='12ASF$$VH2'
SESSION_COOKIE_NAME='OP-TICKET'

##### DB ####
SQLALCHEMY_DATABASE_URI='sqlite:////tmp/test.db'
SQLALCHEMY_TRACK_MODIFICATIONS=True

##### Cache ####
USER_KEY='USERS:%(user_id)s'
Keystone_url='http://127.0.0.1:5000/v2.0'

##### Extra ###
PLAT_LIST='PLAT:list'
PLAT_KEY='PLAT:%(plat_id)s'

GAME_URL='http://127.0.0.1:8334'
GAME_SETTING='GAME:SETTING:%(gameid)s'
GAME_MAXZONE='GAME:MAX_ZONE:%(gameid)s:%(platid)s'
CMD_KEY='CMD:%(category)s:%(gameid)s'
