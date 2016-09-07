#coding:utf-8
import json

from flask import (Blueprint, render_template, request, redirect,
                   url_for, abort)
from flask.ext.login import login_required
from flask.ext.login import current_user as g

from opsticket.models import Ticket, TicketSub
from opsticket.libs import decorator, api

ticket = Blueprint('ticket', __name__)

@ticket.route('/tickets', methods=['GET'])
@decorator.pageination
@login_required
def ticket_list(page, page_size):
    if g.role == 2:
        instance = Ticket.query.filter_by(status=1)
    elif g.role == 1:
        instance = Ticket.query.filter(Ticket.status!=3).filter(Ticket.status!=4).filter_by(platname=g.platname)
    else:
        instance = Ticket.query.filter(Ticket.status!=4).filter_by(user_id=g.id)
    count = instance.count()
    tickets = instance.limit(page_size).offset(page*page_size).all()
    return render_template('tickets/tickets.html', count=count, tickets=tickets, user=g)

@ticket.route('/tickets/create', methods=['GET','POST'])
@login_required
def ticket_create():
    if request.method == 'POST':
        data=request.data
        if data:
            try:
                data=json.loads(data)
            except:
                return redirect(url_for('ticket.ticket_list'))
        else:
            return redirect(url_for('ticket.ticket_list'))
        t=data[0]
        tk=Ticket(app_id=t["app_id"]["value"], appname=t["app_id"]["text"], platname=g.platname,
                plat_id=g.plat_id, category=t["category"]["value"], username=g.account, user_id=g.id)
        tk.save()
        for sub in data:
            ts=TicketSub(target=sub["sid"]["value"], limit_at=sub["limit_at"]["value"], ticket=tk)
            ts.save()
        return redirect(url_for('ticket.ticket_list'))
    return render_template('tickets/add_ticket.html', \
            subject=u"创建工单", \
            user=g)

@ticket.route('/ticket/<int:tid>/info', methods=['GET'])
@login_required
def ticket_info(tid):
    if g.role == 2:
        ts=TicketSub.query.filter_by(ticket_id=tid).all()
    elif g.role == 1:
        if Ticket.query.filter_by(id=tid).filter(plat_id=g.plat_id).first():
            ts=TicketSub.query.filter_by(ticket_id=tid).all()
        else:
            abort(404)
    return render_template('tickets/ticket_info.html', user=g, ts=ts, subject=u"工单详情", tid=tid)

@ticket.route('/ticket/<int:tid>/accept', methods=['POST'])
@login_required
def ticket_accept(tid):
    return json.dumps({"success":True,"msg":u"操作成功"})

@ticket.route('/ticket/<int:tid>/deny', methods=['POST'])
@login_required
def ticket_deny(tid):
    return json.dumps({"success":True,"msg":u"操作成功"})

@ticket.route('/ticket/<int:tid>/revoke', methods=['GET'])
@login_required
def ticket_revoke(tid):
    if g.role == 2:
        t=Ticket.query.filter_by(id=tid).first()
    elif g.role == 1:
        t=Ticket.query.filter_by(id=tid).filter(plat_id=g.plat_id).first()
    else:
        abort(404)
    t.status = 4 #撤销
    t.save()
    return json.dumps({"success":True,"msg":u"撤销成功"})



@ticket.route('/extra/<int:gameid>/zones', methods=['GET'])
@login_required
def extra_zone_list(gameid):
    return json.dumps({"success":True,"msg":api.zone_list(g, gameid)})
