#coding:utf-8
from flask import render_template, request, url_for
from flask.ext.login import login_required, current_user

from opsticket import app
from opsticket.models import User

@app.route('/')
@login_required
def index():
    if current_user.role == 2:
        help_menu = [
            {'icon': "md md-contacts", "name": u"协同账户", "url": "ajax_replace('%s', 'replace_body')" % url_for("user.user_list")},
            {'icon': "md md-settings", "name": u"调度设置", "url": "ajax_replace('%s', 'replace_body')" % url_for("profile.setting_list")},
        ]
        menu = [
            {"icon": "md md-redeem", "name": u"工单审核", "url": "ajax_replace('%s', 'replace_body')" % url_for('ticket.ticket_list')},
        ]
    elif current_user.role == 1:
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
    return render_template("dashboard/dashboard.html", 
            menus=menu, 
            help_menus=help_menu,
            user=current_user)




class Statistic(object):
    def __init__(self, user):
        self.user = user

    def user_count(self):
        if self.user.role == 2:
            return {"text":u"用户总数", "value":User.query.count()}
        elif self.user.role == 1:
            return {"text":u"用户总数", "value":User.query.filter_by(plat_id=self.user.plat_id).count()}
        return {"text":u"用户总数", "value": 1}


