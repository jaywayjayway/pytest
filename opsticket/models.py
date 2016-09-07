#coding:utf-8
import hashlib
import datetime
from flask.ext.login import UserMixin

from opsticket import db


class Model(db.Model):
    __abstract__ = True

    def to_dict(self, hiden=(), show=()):
        ret = {}
        columns = self.__table__.columns.keys()
        for key in columns:
            if key in hiden:
                continue
            if show and key in show:
                ret[key] = getattr(self, key)
                continue
            ret[key] = getattr(self, key)
        return ret

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



class User(Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.Integer)
    platname = db.Column(db.String(100))
    plat_id = db.Column(db.Integer)
    parent = db.Column(db.Integer)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    __tablename__ = 'user'

    def get_id(self):
        return str(self.id)

    @property
    def user_id(self):
        return self.id

    def encryption(self, string):
        return hashlib.md5('YB$a,3'+string+'$$%@cds').hexdigest()

    def __init__(self, account, username, email, password, role, platid): 
        self.account = account
        self.username = username
        self.email = email
        self.password = self.encryption(password)
        self.role = role
        self.plat_id = platid


class App(Model):
    id = db.Column(db.Integer, primary_key=True)
    appname = db.Column(db.String(100))
    app_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('app', lazy='dynamic'))

    __tablename__ = 'app'

class Ticket(Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer)
    appname = db.Column(db.String(100))
    platname = db.Column(db.String(100))
    plat_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=1)  # 1:未处理  2:未通过  3:已处理  
    category = db.Column(db.String(100)) # install  merge
    username = db.Column(db.String(100))
    user_id = db.Column(db.Integer)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime)

    __tablename__ = 'ticket'

class TicketSub(Model):
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(100))
    limit_at = db.Column(db.String(150))
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    ticket = db.relationship('Ticket', backref=db.backref('ticketsub', lazy='dynamic'))

    __tablename__ = 'ticketsub'
