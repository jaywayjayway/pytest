#coding:utf-8
import functools
from flask import abort, request
from flask.ext.login import current_user as g


def pageination(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        try:
            page = int(request.args.get("page", 1)) - 1
            page_size = int(request.args.get("page_size", 15))
        except:
            page = 0
            page_size = 15
        return method(page, page_size, *args, **kwargs)
    return wrapper

def require_admin(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if g.role != 2:
            abort(404)
        return method(*args, **kwargs)
    return wrapper
