#coding:utf-8
import json

from sqlalchemy.sql import or_
from flask import (Blueprint, render_template, request, redirect,
                   url_for, abort, jsonify)
from flask.ext.login import login_required
from flask.ext.login import current_user as g

from opsticket import redis_store, config
from opsticket.models import Ticket, TicketSub
from opsticket.libs import decorator, api, utils

ticket = Blueprint('ticket', __name__)

@ticket.route('/tickets', methods=['GET'])
@login_required
def ticket_list():
    if g.role == 2: 
        instance = Ticket.query.filter(Ticket.status!=3, Ticket.status!=2, Ticket.deleted==False)
    elif g.role == 1:
        instance = Ticket.query.filter(Ticket.status!=3).filter_by(platname=g.platname, deleted=False)
    else:
        instance = Ticket.query.filter(Ticket.status!=3).filter_by(user_id=g.id, deleted=False)
    tickets = instance.all()
    return render_template('tickets/tickets.html', tickets=tickets, user=g)

@ticket.route('/tickets/history', methods=['GET'])
@login_required
def ticket_history():
    if g.role == 2: 
        instance = Ticket.query.filter(or_(Ticket.deleted==True, Ticket.status==3))
    elif g.role == 1:
        instance = Ticket.query.filter_by(platname=g.platname).filter(or_(Ticket.deleted==True, Ticket.status==3))
    else:
        instance = Ticket.query.filter_by(user_id=g.id).filter(or_(Ticket.deleted==True, Ticket.status==3))
    tickets = instance.all()
    return render_template('tickets/tickets.html', tickets=tickets, user=g)


@ticket.route('/tickets/today', methods=['GET'])
@login_required
def today_tickets():
    if g.role == 2:
        between = [utils.now_unix(), utils.tomrrow_work_unix()]
        p = {}
        for i in TicketSub.query.filter(TicketSub.limit_at.between(*between), TicketSub.allow==None).all():
            if i.ticket_id in p:
                continue
            if i.ticket.deleted:
                continue
            p[i.ticket_id] = i.ticket
        tickets = p.values()
    else:
        tickets = []
    return render_template('tickets/tickets.html', tickets=tickets, user=g)

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
    return jsonify({"success":True,"msg":u"工单删除成功!"})

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
            #if tk.category=="install":
            #    max_cache = redis_store.get(config.GAME_MAXZONE % {"gameid":tk.app_id,"platid":tk.plat_id})
            #    if max_cache:
            #        try:
            #            max_cache = int(max_cache)
            #        except:
            #            continue
            #        if max_cache > int(sub["sid"]):
            #            max_value = max_cache
            #    else:
            #        max_value = int(sub["sid"])
            #    redis_store.set(config.GAME_MAXZONE % {"gameid":tk.app_id,"platid":tk.plat_id}, max_value)
        return jsonify({"success":True,"msg":u"工单申请成功!"})
    games = api.setting_list()
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
    return render_template('tickets/ticket_info.html', \
            user=g, ts=ts, t=t, subject=u"工单详情", tid=tid)

@ticket.route('/ticket/<int:tid>/revoke', methods=['GET'])
@login_required
def ticket_revoke(tid):
    if g.role == 2:
        t=Ticket.query.filter_by(id=tid).first()
    elif g.role == 1:
        t=Ticket.query.filter_by(id=tid, plat_id=g.plat_id).first()
    else:
        abort(404)
    if t.ticketsub.filter(TicketSub.allow!=None).count():
        return jsonify({"success":False,"msg":u"工单已经被处理了,请联系审批人撤销!"})
    t.deleted = True #撤销
    t.save()
    return jsonify({"success":True,"msg":u"撤销成功"})


@ticket.route('/ticketsub/<int:tid>/deny/<int:stid>', methods=['POST'])
@login_required
@decorator.require_admin
def ticket_sub_deny(tid, stid):
    t = Ticket.query.filter_by(id=tid).first()
    if not t:
        return jsonify({"success":False,"msg":u"这个工单好像已经被别人处理了,刷新下在看看?"})
    cmd = api.cmdid(g, t.app_id, t.category)
    if not cmd:
        return jsonify({"success":False,"msg":u"你没有批准此类工单的权限!"})
    ts = TicketSub.query.filter_by(id=stid).first()
    ts.allow = False
    ts.save()
    if not t.ticketsub.filter_by(allow=None).first():
        t.status = 2
        t.updated_at = utils.NOW()
        t.save()
    else:
        t.status = 4
        t.updated_at = utils.NOW()
        t.save()
    return jsonify({"success":True,"msg":u"操作成功","data":ts.to_dict(hiden=['created_at','updated_at'])})

@ticket.route('/ticket/accept/<int:tid>/all', methods=['POST'])
@login_required
@decorator.require_admin
def ticket_allow_all(tid):
    t=Ticket.query.filter_by(id=tid).first()
    if not t:
        return jsonify({"success":False,"msg":u"工单不存在"})
    cmd = api.cmdid(g, t.app_id, t.category)
    if not cmd:
        return jsonify({"success":False,"msg":u"你没有批准此类工单的权限!"})
    if not t.ticketsub.filter_by(allow=None).count():
        return jsonify({"success":False,"msg":u"该工单已经处理完了!"})
    
    if t.category == "install":
        #装服
        sdata=api.host_scheduler(g, t.app_id, t) or {}
        if not sdata:
            return jsonify({"success":False,"msg":u"服务器库存不够了,无法通过审批,抓紧联系OPS!"})
        if sdata == 2333:
            return jsonify({"success":False,"msg":u"尚未配置调度参数,请联系OPS配置!"})
        uuid = utils.get_uuid()
        cache_msg={"msg":sdata, "tid":tid}
        redis_store.set(config.SCHEDULER_ID % locals(), json.dumps(cache_msg))
        if not sdata or len(sdata) != t.ticketsub.filter_by(allow=None).count():
            #服务器不够,返回一个callback
            nop = []
            for tc in t.ticketsub.filter_by(allow=None).all():
                if utils.now_unix() + 300 > int(ts.limit_at):
                    return jsonify({"success":False,"msg":"工单里有任务已经过期, 请先拒绝掉过期任务!"})
                if not sdata or str(tc.target) not in sdata:
                    nop.append({"sid":str(tc.target)})
            yesp = []
            for sid,ip in sdata.items():
                yespa.append({"sid":sid,"ip":ip})
            #return jsonify({"success":False, "msg":{"no":nop,"yes": [{"sid":1,"ip":"1.1.1.1"}], "uuid":uuid}, "callback":"/ticket/%s/block" % tid})
            msg = {"no":nop, "yes":yesp, "uuid":uuid}
            return jsonify({"success":False, "msg":msg, "callback":"/ticket/%s/block" % tid})
        p = {}
        for ts in t.ticketsub.filter_by(allow=None).all():
            if utils.now_unix() + 300 > int(ts.limit_at):
                return jsonify({"success":False,"msg":"工单里有任务已经过期, 请先拒绝掉过期任务!"})
            sid=str(ts.target)
            ip=sdata.get(sid, None)
            if ip in p:
                p[ip] += ',%s' % sid
            else:
                p[ip] = sid
            if not ip:
                continue
        ext = {"install":p}
    else:
        #合服
        ts = t.ticketsub.first()
        sids = [i for i in ts.target.split(",") if i ]
        sids = map(int, sids)
        ext = {"merge": "%s-%s" % (min(sids), max(sids)), "crontime": ts.limit_at}

    if api.send_cmd(g, cmd, t, ext):
        for ts in t.ticketsub.all():
            ts.allow = True
            ts.save()
        if t.ticketsub.filter_by(allow=None).first():
            t.status = 4
            t.updated_at = utils.NOW()
            t.save()
        else:
            t.status = 3
            t.updated_at = utils.NOW()
            t.save()
        return jsonify({"success":True,"msg":u"操作成功","data":ts.to_dict()})

@ticket.route('/ticket/<int:tid>/block', methods=['GET'])
@login_required
@decorator.require_admin
def ticket_block(tid):
    return render_template('tickets/accept_confitm.html', subject=u"工单批准确认", user=g)

@ticket.route('/ticket/confirm/<string:uuid>', methods=['GET'])
@login_required
@decorator.require_admin
def ticket_confirm(uuid):
    cache_msg = redis_store.get(config.SCHEDULER_ID % locals())
    try:
        cache_msg = json.loads(cache_msg)
    except:
        return jsonify({"success":False,"msg":u"分配信息已失效,请重新审核!"})
    tid = cache_msg["tid"]
    msg = cache_msg["msg"]
    t = Ticket.query.filter_by(id=tid).first()
    cmd = api.cmdid(g, t.app_id, t.category)
    if not cmd:
        return jsonify({"success":False,"msg":u"你没有批准此类工单的权限!"})
    p={}
    for sid, ip in msg.items():
        if ip in p:
            p[ip] += ",%s" % sid
        else:
            p[ip] = str(sid)
    ext = {"install": p}
    if api.send_cmd(g, cmd, t, ext):
        redis_store.delete(config.SCHEDULER_ID % locals())
        for ts in t.ticketsub.filter(TicketSub.target.in_(list(msg))).all():
            ts.allow=True
            ts.save()
        if t.ticketsub.filter_by(allow=None).first():
            t.status=4
            t.updated_at = utils.NOW()
        else:
            t.status=3
            t.updated_at = utils.NOW()
        t.save()
        return jsonify({"success":True,"msg":u"工单批准成功!"})
    return jsonify({"success":False,"msg":u"工单批准失败!"})

@ticket.route('/ticketsub/<int:tid>/allow/<int:stid>', methods=['POST'])
@login_required
@decorator.require_admin
def ticket_sub_allow(tid, stid):
    ts = TicketSub.query.filter_by(id=stid).first()
    print ts.limit_at, utils.now_unix()
    if utils.now_unix() + 300 > int(ts.limit_at):
        return jsonify({"success":False,"msg":"该子任务已经过期, 请拒绝掉过期任务!"})

    if ts.ticket.category == "install":
        msg=api.host_scheduler(g, ts.ticket.app_id, ts)
        if not msg:
            return jsonify({"success":False,"msg":u"服务器库存不够了,无法通过审批,抓紧联系OPS!"})
        if msg == 2333:
            return jsonify({"success":False,"msg":u"尚未配置调度参数,请联系OPS配置!"})
        p={}
        for sid, ip in msg.items():
            if ip in p:
                p[ip] += ",%s" % sid
            else:
                p[ip] = str(sid)
        ext = {"install": p}
    else:
        try:
            p = map(int, ts.target.split(","))
        except:
            return jsonify({"success":False,"msg":u"该请求数据非法~联系下管理员!"})
        for index, v in enumerate(sorted(p)):
            if index == 0:
                continue
            if v - sorted(p)[index-1] != 1:
                return jsonify({"success":False,"msg":u"该合服数据非法~联系下管理员!"})
        ext = {"merge": "%s-%s" % (min(p), max(p)), "crontime": ts.limit_at}
    cmdid = api.cmdid(g, ts.ticket.app_id, ts.ticket.category)
    if not cmdid:
        return jsonify({"success":False,"msg":u"你没有批准此类工单的权限!"})
    if api.send_cmd(g, cmdid, ts.ticket, ext):
        ts.allow = True
        ts.save()
        t = Ticket.query.filter_by(id=tid).first()
        if not t.ticketsub.filter_by(allow=None).first():
            t.status = 3
            t.save()
            t.updated_at = utils.NOW()
        else:
            t.status = 4
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
    if msg == 2333:
        return jsonify({"success":False,"msg":u"尚未配置调度参数,请联系OPS配置!"})
    return jsonify({"success":True,"msg":msg})
