#coding:utf-8
import json

from flask import flash, Blueprint, render_template, request, redirect, session
from flask.ext.login import login_user, logout_user
from opsticket.models import User
from opsticket.libs import keystone, utils

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        remember = request.form.get("remember", "")
        user = User.query.filter_by(username=username).first()
        if user and user.password == utils.encryption(password):
            session.permanent = True
            if remember == 'on':
                login_user(user, remember=True)
            else:
                login_user(user)
            return redirect('/')
        flash(u'用户名或密码错误!')
    return render_template('login.html')

@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash(u'登出成功!')
    return redirect('/login')

@auth.route('/admin/login', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        remember = request.form.get("password", "")
        user = keystone.authentication(username, password)
        if user:
            session.permanent = True
            if remember == 'on':
                login_user(user, remember=True)
            else:
                login_user(user)
            login_user(user)
            return redirect('/')
        flash(u'用户名或密码错误!')
    return render_template('admin.html')
