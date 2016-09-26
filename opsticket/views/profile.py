#coding:utf-8
import json

from flask import Blueprint, render_template, abort, request, jsonify, url_for
from flask.ext.login import login_required, current_user as g

from opsticket.models import User
from opsticket import redis_store, config
from opsticket.libs import decorator, api, utils

profile = Blueprint('profile', __name__)

@profile.route('/profiles', methods=['GET'])
@login_required
@decorator.require_admin
def setting_list():
    keys = redis_store.keys("GAME:SETTING:*")
    data = []
    for key in keys:
        data.append(json.loads(redis_store.get(key)))
    return render_template("profile/profiles.html", user=g, ss=data)


@profile.route('/profile/create', methods=['GET', 'POST'])
@login_required
@decorator.require_admin
def setting_create():
    if request.method == 'POST':
        gameid = request.form.get("app_id", None)
        data = request.form.to_dict()
        if redis_store.get(config.GAME_SETTING % locals()):
            return jsonify({"success":False,"msg":u"该游戏已经设置过了,请进行更新操作!"})
        redis_store.set(config.GAME_SETTING % locals(), json.dumps(data))
        return jsonify({"success":True,"msg":u"游戏设置成功!"})

    owner_game = api.profile_game(g)
    return render_template("profile/create.html", user=g, games=owner_game, s=None,\
            subject=u"添加游戏设置", url=url_for('profile.setting_create'))


@profile.route('/profile/<int:gameid>/update', methods=['GET', 'POST'])
@login_required
@decorator.require_admin
def setting_update(gameid):
    if request.method == 'POST':
        data = request.form.to_dict()
        if not redis_store.get(config.GAME_SETTING % locals()):
            return jsonify({"success":False,"msg":u"该游戏尚未设置过,请进行添加操作!"})
        redis_store.set(config.GAME_SETTING % locals(), json.dumps(data))
        return jsonify({"success":True,"msg":u"游戏更新成功!"})

    owner_game = api.profile_game(g, gameid)
    s = json.loads(redis_store.get(config.GAME_SETTING % locals()))
    return render_template("profile/create.html", user=g, games=owner_game, s=s, \
            subject=u"更新游戏设置", url=url_for('profile.setting_update', gameid=gameid))

@profile.route('/profile/<int:gameid>/delete', methods=['DELETE'])
@login_required
@decorator.require_admin
def setting_delete(gameid):
    redis_store.delete(config.GAME_SETTING % locals())
    return jsonify({"success":True,"msg":u"游戏配置删除成功!"})
