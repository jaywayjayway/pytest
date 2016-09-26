#coding:utf-8
import json

from flask import (Blueprint, render_template, request, redirect,
                   url_for, abort, jsonify)
from flask.ext.login import login_required
from flask.ext.login import current_user as g

from opsticket import redis_store, config
from opsticket.models import Ticket, TicketSub
from opsticket.libs import decorator, api, utils

ticket = Blueprint('ticket', __name__)

@ticket.route('/tickets', methods=['GET'])
@decorator.pageination
@login_required
def ticket_list(page, page_size):
    if g.role == 2:
        instance = Ticket.query.filter_by(status=1, deleted=False)
    elif g.role == 1:
        instance = Ticket.query.filter(Ticket.status!=3).filter(Ticket.status!=4).filter_by(platname=g.platname, deleted=False)
    else:
        instance = Ticket.query.filter(Ticket.status!=4).filter_by(user_id=g.id, deleted=False)
    count = instance.count()
    tickets = instance.limit(page_size).offset(page*page_size).all()
    return render_template('tickets/tickets.html', count=count, tickets=tickets, user=g)


@ticket.route('/install/request', methods=['GET'])
@login_required
def install_request():
    return render_template('tickets/install.html', subject=u"装服申请")


@ticket.route('/merge/request', methods=['GET'])
@login_required
def merge_request():
    return render_template('tickets/merge.html', subject=u"合服申请")


@ticket.route('/tickets/<int:tid>/delete', methods=['DELETE'])
@login_required
def ticket_delete(tid):
    if g.role == 1:
        t = Ticket.query.filter_by(id=tid, plat_id=g.plat_id).first()
    else:
        t = Ticket.query.filter_by(id=tid, user_id=g.id).first()
    if not t:
        return jsonify({"success":False,"msg":u"工单不存在!"})
    t.deleted=True
    t.save()
    return jsonify({"success":False,"msg":u"工单删除成功!"})



@ticket.route('/tickets/create', methods=['GET','POST'])
@login_required
def ticket_create():
    if request.method == 'POST':
        data=request.form
        if data:
            try:
                data=data.to_dict()
                json.loads(data["children"])
            except Exception,e:
                return jsonify({"success":False,"msg":u"你提交的数据不合法呀!"})
        else:
            return jsonify({"success":False,"msg":u"你提交的数据不合法呀!"})
        tk=Ticket(app_id=data["app_id"], appname=data["appname"], platname=g.platname,
                plat_id=g.plat_id, category=data["category"], username=g.account, user_id=g.id)
        tk.save()
        for sub in json.loads(data["children"]):
            ts=TicketSub(target=sub["sid"], limit_at=sub["limit"], ticket=tk)
            ts.save()
            if tk.category=="install":
                max_cache = redis_store.get(config.GAME_MAXZONE % {"gameid":tk.app_id,"platid":tk.plat_id})
                if max_cache:
                    try:
                        max_cache = int(max_cache)
                    except:
                        continue
                    if max_cache > int(sub["sid"]):
                        redis_store.set(config.GAME_MAXZONE % {"gameid":tk.app_id,"platid":tk.plat_id}, sub["sid"])
        return jsonify({"success":True,"msg":u"工单申请成功!"})
    if g.role >= 1:
        games = api.game_list(g)
    else:
        games = []
    return render_template('tickets/add_ticket.html', \
            subject=u"创建工单", \
            user=g, games=games)

@ticket.route('/ticket/<int:tid>/info', methods=['GET'])
@login_required
def ticket_info(tid):
    if g.role == 2:
        ts=TicketSub.query.filter_by(ticket_id=tid).all()
    elif g.role == 1:
        if Ticket.query.filter_by(id=tid, plat_id=g.plat_id).first():
            ts=TicketSub.query.filter_by(ticket_id=tid).all()
        else:
            abort(404)
    else:
        ts=Ticket.query.filter_by(id=tid, user_id=g.id).first()
        if ts:
            ts = ts.ticketsub.all()
        else:
            abort(404)
    t = Ticket.query.filter_by(id=tid).first()
    if t and t.category == "install" and g.role == 2:
        groups = api.group_list(g, t.app_id)
    else:
        groups = []
    return render_template('tickets/ticket_info.html', \
            user=g, ts=ts, t=t, subject=u"工单详情", tid=tid, \
            groups=groups)

@ticket.route('/ticket/<int:tid>/revoke', methods=['GET'])
@login_required
def ticket_revoke(tid):
    if g.role == 2:
        t=Ticket.query.filter_by(id=tid).first()
    elif g.role == 1:
        t=Ticket.query.filter_by(id=tid, plat_id=g.plat_id).first()
    else:
        abort(404)
    t.status = 4 #撤销
    t.save()
    return jsonify({"success":True,"msg":u"撤销成功"})


@ticket.route('/ticketsub/<int:tid>/deny/<int:stid>', methods=['POST'])
@login_required
@decorator.require_admin
def ticket_sub_deny(tid, stid):
    ts = TicketSub.query.filter_by(id=stid).first()
    ts.allow = False
    ts.save()
    t = Ticket.query.filter_by(id=tid).first()
    if not t.ticketsub.filter_by(allow=None).first():
        t.status = 2
        t.save()
    return jsonify({"success":True,"msg":u"操作成功","data":ts.to_dict(hiden=['created_at','updated_at'])})

@ticket.route('/ticketsub/<int:tid>/allow/<int:stid>', methods=['POST'])
@login_required
@decorator.require_admin
def ticket_sub_allow(tid, stid):
    ts = TicketSub.query.filter_by(id=stid).first()
    if ts.ticket.category == "install":
        sid = request.form.get("sid", None)
        ip = request.form.get("ip", None)
        if not (sid and ip):
            return jsonify({"success":False,"msg":u"没有分配的IP无法通过批准!"})
        ext = {"install": {ip:str(sid)}, "crontime": int(ts.limit_at)-7200}
    else:
        try:
            p = map(int, ts.target.split(","))
        except:
            return jsonify({"success":False,"msg":u"该请求数据非法~联系下管理员!"})
        for index, v in enumerate(sorted(p)):
            if index == 0:
                continue
            if v - sorted(p)[index-1] != 1:
                return jsonify({"success":False,"msg":u"该请求数据非法~联系下管理员!"})
        ext = {"merge_str": "%s-%s" % (min(p), max(p)), "crontime": ts.limit_at}
    cmdid = api.cmdid(g, ts.ticket.app_id, ts.ticket.category)
    if not cmdid:
        return jsonify({"success":False,"msg":u"你没有批准此类工单的权限!"})
    if api.send_cmd(g, cmdid, ts.ticket, ext):
        ts.allow = True
        ts.save()
        t = Ticket.query.filter_by(id=tid).first()
        if not t.ticketsub.filter_by(allow=None).first():
            t.status = 2
            t.save()
        return jsonify({"success":True,"msg":u"操作成功","data":ts.to_dict()})
    return jsonify({"success":False,"msg":u"审核失败~联系下管理员!"})

@ticket.route('/ticketsub/<int:tid>/revoke/<int:stid>', methods=['POST'])
@login_required
def ticket_sub_revoke(tid, stid):
    if g.role < 1:
        t = Ticket.query.filter_by(id=tid, user_id=g.id).first()
    else:
        t = Ticket.query.filter_by(id=tid, plat_id=g.plat_id).first()
    if not t:
        abort(404)
    ts = TicketSub.query.filter_by(id=stid).first()
    ts.delete()
    if t.ticketsub.count() == 0:
        t.delete()
    return jsonify({"success":True,"msg":u"工单撤销成功!"})


@ticket.route('/extra/<int:gameid>/zones', methods=['GET'])
@login_required
def extra_zone_list(gameid):
    return jsonify({"success":True,"msg":api.zone_list(g, gameid)})

@ticket.route('/extra/<int:gameid>/zonelimit', methods=['GET'])
@login_required
def extra_zone_limit(gameid):
    max_cache = redis_store.get(config.GAME_MAXZONE % {"gameid":gameid,"platid":g.plat_id})
    if max_cache:
        if int(max_cache) > int(api.zone_limit(g, gameid)):
            return jsonify({"success":True,"msg":int(max_cache)})
    return jsonify({"success":True,"msg":api.zone_limit(g, gameid)})

@ticket.route('/extra/<int:gameid>/grouplist', methods=['GET'])
@login_required
@decorator.require_admin
def extra_group_list(gameid):
    return jsonify({"success":True,"msg":api.group_list(g, gameid)})

@ticket.route('/extra/<int:tid>/distributionip', methods=['POST'])
@login_required
@decorator.require_admin
def extra_distributionip(tid):
    t = Ticket.query.filter_by(id=tid).first()
    gameid = request.form.get("gameid", None)
    groupid = request.form.get("groupid", None)
    if not t.ticketsub.filter_by(allow=None).first():
        return jsonify({"success":False,"msg":u"工单不存在或已经被处理了!"})
    if not gameid:
        return jsonify({"success":False,"msg":u"参数不完整!"})
    msg = api.host_scheduler(g, gameid, t)
    if not msg:
        return jsonify({"success":False,"msg":u"调度失败,可用的服务器不足!"})
    return jsonify({"success":True,"msg":msg})
