#coding:utf-8
import json

from flask import Blueprint, render_template, abort, request, jsonify
from flask.ext.login import login_required, current_user as g

from opsticket.models import User
from opsticket.libs import decorator, api, utils

user = Blueprint('user', __name__)

@user.route('/users', methods=['GET'])
@decorator.pageination
@login_required
def user_list(page, page_size):
    instance = User.query
    if g.role == 2:
        pass
    elif g.role == 1:
        instance = instance.filter_by(parent=g.user_id)
    else:
        abort(404)
    count = instance.count()
    users = instance.limit(page_size).offset(page*page_size).all()
    return render_template('users/users.html', count=count, data=users)

@user.route('/users/create', methods=['GET', 'POST'])
@login_required
def user_create():
    if request.method == 'POST':
        account = request.form.get("account", None)
        username = request.form.get("username", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        platid = request.form.get("platid", None)
        if not (account and username and email and password):
            return json.dumps({"success":False, "msg":u"缺少参数!"})
        if g.role == 2:
            role = 1
        elif g.role == 1:
            role = 0
        else:
            return json.dumps({"success":False, "msg":u"你没有权限!"})
        user = User(account, username, email, password, role, platid)
        user.save()
        return json.dumps({"success":True, "msg":u"添加用户成功","data":user.to_dict(hiden=['password'])}, cls=utils.ComplexEncoder)

    plats = api.plat_list()
    games = []
    if g.role == 1:
        games = api.game_list(g)
    return render_template('users/user_form.html', 
            plats=plats,
            games=games,
            subject=u"添加用户",
            user=g)

@user.route('/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
def user_delete(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return json.dumps({"success":False,"msg":u"用户已经不存在了!"})
    if g.role == 2:
        user.delete()
    elif g.role == 1:
        if user.role == 0:
            user.delete()
        else:
            return json.dumps({"success":False,"msg":u"你没有权限!"})
    else:
        return json.dumps({"success":False,"msg":u"你没有权限!"})
    return json.dumps({"success":True,"msg":u"用户删除成功!"})
