#coding:utf-8
import re
import pickle
from datetime import timedelta

from . import config
from .extra import filters

from flask import Flask

from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.redis import FlaskRedis

app = Flask(__name__)
app.config.from_object(config)
app.jinja_env.filters['datetime'] = filters.dateformat

redis_store = FlaskRedis(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = u"请登录！"
login_manager.remember_cookie_duration=timedelta(hours=10)
login_manager.session_protection = "strong"

db = SQLAlchemy(app)

from opsticket.views import *

app.register_blueprint(auth)
app.register_blueprint(ticket)
app.register_blueprint(user)

app.secret_key = 'A0Zr98j/3yX R~@e23'
app.permanent_session_lifetime = timedelta(hours=8)

from opsticket.models import User

def like_uuid(val):
    if re.match(r'(\w){32}', val):
        return True
    return False

@login_manager.user_loader
def load_user(user_id):
    if like_uuid(user_id):
        user = redis_store.get(config.USER_KEY % {"user_id":user_id})
        if user:
            return pickle.loads(user)["user"]
        return None
    return User.query.filter_by(id=user_id).first()
