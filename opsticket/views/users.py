#coding:utf-8
import json

from flask import Blueprint, render_template, abort, request, jsonify, url_for
from flask.ext.login import login_required, current_user as g

from opsticket import redis_store, config
from opsticket.models import User, App
from opsticket.libs import decorator, api, utils

user = Blueprint('user', __name__)

@user.route('/users', methods=['GET'])
@login_required
def user_list():
    instance = User.query
    if g.role == 2:
        instance = instance.filter_by(role=1)
    elif g.role == 1:
        instance = instance.filter_by(plat_id=g.plat_id, role=0)
    else:
        abort(404)
    count = instance.count()
    users = instance.all()
    return render_template('users/users.html', count=count, data=users)

@user.route('/users/create', methods=['GET', 'POST'])
@login_required
def user_create():
    if request.method == 'POST':
        account = request.form.get("account", None)
        username = request.form.get("username", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        if not utils.complexity_check(password):
            return jsonify({"success":False, "msg":u"密码长度至少8位以上,并包含大小写字母及数字!"})
        if g.role == 2:
            platid = request.form.get("platid", None)
        else:
            platid = g.plat_id
        apps = request.form.getlist("apps")
        if not (account and username and email and password):
            return jsonify({"success":False, "msg":u"缺少参数!"})
        plat = api.plat_info(platid)
        if not plat:
            return jsonify({"success":False, "msg":u"平台不存在呀!"})
        if g.role == 2:
            role = 1
            user = User(account, username, email, password, role, platid, plat["platename"])
            user.save()
        elif g.role == 1:
            role = 0
            user = User(account, username, email, password, role, platid, plat["platename"])
            user.save()
            for app in apps:
                app_cache = redis_store.get(config.GAME_INFO % {"gameid":app})
                if not app_cache:
                    continue
                app_cache = json.loads(app_cache)
                a = App(app_id=app, user=user, appname=app_cache["appname"])
                a.save()
        else:
            return jsonify({"success":False, "msg":u"你没有权限!"})
        return jsonify({"success":True, "msg":u"添加用户成功"})

    plats = api.plat_list()
    tu = None
    games = api.setting_list()
    return render_template('users/user_form.html', 
            plats=plats,
            games=games,
            subject=u"添加用户",
            user=g, tu=tu,
            url=url_for('user.user_create'))

@user.route('/users/<int:uid>/update', methods=['GET', 'POST'])
@login_required
def user_update(uid):
    if request.method == 'POST':
        account = request.form.get("account", None)
        username = request.form.get("username", None)
        email = request.form.get("email", None)
        if g.role == 2:
            platid = request.form.get("platid", None)
        else:
            platid = g.plat_id
        apps = request.form.getlist("apps")
        plat = api.plat_info(platid)
        if not plat:
            return jsonify({"success":False, "msg":u"平台不存在呀!"})

        user = User.query.filter_by(id=uid).first()
        if not user:
            return jsonify({"success":False,"msg":u"用户不存在"})
        user.account = account
        user.username = username
        user.email = email
        user.platid = platid
        user.platname = plat["platename"]
        user.save()
        
        exists = [i[0] for i in user.app.values('app_id')]
        need_add = set(apps) - set(exists)
        need_del = set(exists) - set(apps)
        for add in need_add:
            app_cache = redis_store.get(config.GAME_INFO % {"gameid":add})
            if not app_cache:
                continue
            app_cache = json.loads(app_cache)
            a = App(app_id=add, user=user, appname=app_cache["appname"])
            a.save()
        for del_a in need_del:
            a = App.query.filter_by(app_id=del_a, user=user).first()
            a.delete()

        return jsonify({"success":True,"msg":u"用户更新成功!"})


    plats = api.plat_list()
    tu = None
    if g.role == 1:
        tu = User.query.filter_by(id=uid, plat_id=g.plat_id).first()
    elif g.role == 2:
        tu = User.query.filter_by(id=uid).first()
    games = api.setting_list()
    return render_template('users/user_form.html', 
            plats=plats,
            games=games,
            subject=u"更新用户",
            user=g, tu=tu,
            url=url_for('user.user_update', uid=uid))

@user.route('/users/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        old_password = request.form.get("old_password", None)
        new_password = request.form.get("new_password", None)
        confirm_password = request.form.get("confirm_password", None)
        if not utils.complexity_check(new_password):
            return jsonify({"success":False, "msg":u"密码长度至少8位以上,并包含大小写字母及数字!"})
        if g.password == utils.encryption(old_password):
            if new_password != confirm_password:
                return jsonify({"success":False,"msg":u"两次输入的密码不一致!"})
            g.password = utils.encryption(new_password)
            g.save()
            return jsonify({"success":True,"msg":u"个人配置成功!"})
        return jsonify({"success":False,"msg":u"旧密码不正确!"})

    return render_template('users/user_profile.html', subject=u"个人配置")

@user.route('/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
def user_delete(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success":False,"msg":u"用户已经不存在了!"})
    if g.role == 2:
        user.delete()
    elif g.role == 1:
        if user.role == 0:
            user.delete()
        else:
            return jsonify({"success":False,"msg":u"你没有权限!"})
    else:
        return jsonify({"success":False,"msg":u"你没有权限!"})
    return jsonify({"success":True,"msg":u"用户删除成功!"})