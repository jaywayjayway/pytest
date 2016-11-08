#coding:utf-8
import random
from flask import render_template, request, url_for
from flask.ext.login import login_required
from flask.ext.login import current_user as g

from opsticket import app
from opsticket.libs import utils
from opsticket.models import User, Ticket, TicketSub

@app.route('/')
@login_required
def index():
    if g.role == 2:
        help_menu = [
            {'icon': "md md-contacts", "name": u"平台账户", "url": "ajax_replace('%s', 'replace_body')" % url_for("user.user_list")},
        ]
        menu = [
            {"icon": "md md-alarm", "name": u"今日待办", "url": "ajax_replace('%s', 'replace_body')" % url_for('ticket.today_tickets')},
            {"icon": "md md-redeem", "name": u"工单审核", "url": "ajax_replace('%s', 'replace_body')" % url_for('ticket.ticket_list')},
        ]
    elif g.role == 1:
        help_menu = [
            {'icon': "md md-contacts", "name": u"协同账户", "url": "ajax_replace('%s', 'replace_body')" % url_for("user.user_list")},
        ]
        menu = [
            {"icon": "md md-redeem", "name": u"工单申请", "url": "ajax_replace('%s', 'replace_body')" % url_for('ticket.ticket_list')},
        ]
    else:
        help_menu = []
        menu = [
            {"icon": "md md-redeem", "name": u"工单申请", "url": "ajax_replace('%s', 'replace_body')" % url_for('ticket.ticket_list')},
        ]

    menu.append({"icon":"md md-history","name":u"历史工单","url":"ajax_replace('%s', 'replace_body')" % url_for('ticket.ticket_history')})
    if g.isadmin:
        help_menu.append({'icon': "md md-settings", "name": u"调度设置", "url": "ajax_replace('%s', 'replace_body')" % url_for("profile.setting_list")})
    return render_template("dashboard/dashboard.html", 
            menus=menu, 
            help_menus=help_menu,
            user=g,
            graph=Statistic())


class Statistic(object):
    def __init__(self):
        self.install = 0
        self.merge = 0
        self.count = 0

        self.init()

    def init(self):
        between = [utils.now_unix(), utils.tomrrow_work_unix()]
        if g.role == 2:
            base = Ticket.query.filter_by(deleted=False)
        elif g.role == 1:
            base = Ticket.query.filter_by(deleted=False, platname=g.platname)
        else:
            base = Ticket.query.filter_by(deleted=False, user_id=g.id)
        base = base.filter(Ticket.status!=2, Ticket.status!=3).all()
        for t in base:
            self.count += 1
            for i in t.ticketsub.filter(TicketSub.limit_at.between(*between)).all():
                if i.target == 'install' and i.allow is None:
                    self.install += 1
                if i.target == 'merge' and i.allow is None:
                    self.merge += 1

    def user_count(self):
        if g.role == 2:
            return {"text":u"用户总数", "value":User.query.count(), "than":random.randint(2,90)}
        elif g.role == 1:
            return {"text":u"用户总数", "value":User.query.filter_by(plat_id=g.plat_id).count()-1, "than":random.randint(2,90)}
        return {"text":u"用户总数", "value": 1, "than":random.randint(2,90)}

    def today_job(self):
        return {"text":u"今日待办", "value": self.count, "than":random.randint(2,90)}

    def install_job(self):
        return {"text":u"今日装服", "value": self.install, "than":random.randint(2,90)}

    def merge_job(self):
        return {"text":u"今日合服", "value": self.merge, "than":random.randint(2,90)}


