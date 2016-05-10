import tornado.template
import tornado.gen
import tornado.web
import tornado.ioloop
import tornado.websocket

import momoko
import json
import logging
import datetime
import inspect
import types
from urllib.parse import quote

from utils.include import include
from utils.log import log
from utils.form import form_validation
import myredis
import config


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class Service:
    db = momoko.Pool(
            **config.DB_SETTING
            )
    future = db.connect()
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.add_future(future, lambda f, io_loop=io_loop: io_loop.stop())
    io_loop.start()

    rs = myredis.MyRedis(
            **config.REDIS_SETTING
            )
    form_validation = form_validation
    log = log


def Service_init():
    include(Service, './service', ['base.py'], True)


class Handler:
    pass


def Handler_init():
    include(Handler, './handler', ['base.py'], False)


class Permission:
    pass


def Permission_init():
    include(Permission, './permission', ['base.py'], False)


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = log

    def get_args(self, name):
        meta = {}
        for n in name:
            try:
                if n[-2:] == "[]":
                    meta[n[:-2]] = self.get_arguments(n)
                elif n[-6:] == "[file]":
                    n = n[:-6]
                    meta[n] = self.request.files[n][0]
                else:
                    meta[n] = self.get_argument(n)
            except:
                meta[n] = None
        return meta

    @tornado.gen.coroutine
    def check_permission(self):
        now = Permission
        for attr in self.path:
            if not hasattr(now, attr):
                return None
            else:
                now = getattr(now, attr)
        method = self.request.method.lower()
        if not hasattr(now, method):
            return None
        res = getattr(now, method)(self)
        if isinstance(res, types.GeneratorType):
            res = yield from res
        return res

    @tornado.gen.coroutine
    def prepare(self):
        super().prepare()
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        self.remote_ip = remote_ip
        self.log("[%s] %s %s" % (
                 self.request.method, self.request.uri, self.remote_ip))


class ApiRequestHandler(RequestHandler):
    def render(self, msg=""):
        if isinstance(msg, tuple):
            code, msg = msg
        else:
            code = 200
        self.set_status(code)
        self.finish(json.dumps({
                'msg': msg
            },
            cls=DatetimeEncoder))
        return

    @tornado.gen.coroutine
    def prepare(self):
        res = yield super().prepare()
        res = yield super().check_permission()
        print(res)
        if res:
            self.render(res)
            return


class WebRequestHandler(RequestHandler):
    def set_secure_cookie(self, name, value,
                          expires_days=30, version=None, **kwargs):
        kwargs['httponly'] = True
        super().set_secure_cookie(name, value, expires_days, version, **kwargs)

    def write_error(self, err, **kwargs):
        try:
            status_code, err = err
        except:
            status_code, err = err, ''
        kwargs['err'] = err
        self.set_status(status_code)
        self.render('./web/template/err/'+str(status_code)+'.html', **kwargs)

    def render(self, templ, **kwargs):
        super().render('./web/template/'+templ, **kwargs)

    @tornado.gen.coroutine
    def prepare(self):
        res = yield super().prepare()
        res = yield super().check_permission()
        if res:
            self.write_error(res)
            return


class StaticFileHandler(tornado.web.StaticFileHandler):
    @tornado.gen.coroutine
    def prepare(self):
        super().prepare()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
