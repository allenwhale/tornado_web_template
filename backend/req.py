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
from utils.log import log
import momoko
import config
import types
import re
from utils.form import form_validation
from utils.utils import *
from utils.include import *
from urllib.parse import quote
import sys

from utils.include import include
from utils.log import log
from utils.form import form_validation
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

    form_validation = form_validation
    log = log


def Service_init():
    include(Service, './service', ['base.py'], True)


class Handler:
    pass

def Service__init__():
    ##################################################
    ### Setting db                                 ###
    ##################################################
    db = momoko.Pool(**config.DB_SETTING)
    future = db.connect()
    tornado.ioloop.IOLoop.instance().add_future(future, lambda f: tornado.ioloop.IOLoop.instance().stop())
    tornado.ioloop.IOLoop.instance().start()
    ##################################################
    ### Setting Service                            ###
    ##################################################
    Service.db = db
    Service.log = log
    Service.form_validation = form_validation
    ##################################################
    ### Importing Service Module                   ###
    ##################################################
    include(Service, "./service", ["base.py"], True, False)
    Service.Permission = T()
    include(Service.Permission, "./permission/", ["base.py"], True, True)

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

    def set_secure_cookie(self, name, value, expires_days=30, version=None, **kwargs):
        kwargs['httponly'] = True
        super().set_secure_cookie(name, value, expires_days, version, **kwargs)

    @tornado.gen.coroutine
    def check_permission(self):
        now = Service.Permission
        for attr in self.path[1:]:
            if hasattr(now, attr):
                now = getattr(now, attr)
            else:
                return None
        method = self.request.method.lower()
        if not hasattr(now, method):
            return None
        res = getattr(now, method)(self, *self.path_args, **self.path_kwargs)
        if isinstance(res, types.GeneratorType):
            res = yield from res
        return res

    @tornado.gen.coroutine
    def prepare(self):
        ##################################################
        ### Get IP                                     ###
        ##################################################
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        self.remote_ip = remote_ip
        self.log("[%s] %s %s"%(self.request.method, self.request.uri, self.remote_ip))
        ##################################################
        ### Get Identity                               ###
        ##################################################
        yield self.get_identity()
        ##################################################
        ### Check Permission                           ###
        ##################################################

    @tornado.gen.coroutine
    def get_identity(self):
        cookie_token = self.get_secure_cookie('token')
        token = None
        if cookie_token is None:
            ### get by token
            token = self.get_args(['token'])['token']
        else:
            ### get by cookies
            try:
                token = cookie_token.decode()
            except:
                token = None

        if token:
            err, res = yield from Service.Session.signin_by_token(self, {'token': token})
            if err:
                self.account = {}
                self.clear_cookie('token')
            else:
                self.account = res
        else:
            self.account = {}

class ApiRequestHandler(RequestHandler):
    def render(self, msg=""):
        if isinstance(msg, tuple):
            code, msg = msg
        else:
            code = 200
        self.set_status(code)
        try:
            msg = json.dumps({
                'msg': msg
            }, cls=DatetimeEncoder)
        except:
            msg = str(msg)
        self.finish(msg)

    def write_error(self, err, **kwargs):
        self.log(err)
        self.log(kwargs)
        self.render((err, kwargs))

    @tornado.gen.coroutine
    def prepare(self):
        res = yield super().prepare()
        msg = yield self.check_permission()
        if msg is not None:
            self.render(msg)

class WebRequestHandler(RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.render('./err/%s.html'%(status_code,), **kwargs)

    def render(self, templ, **kwargs):
        kwargs['title'] = self.title
        kwargs['account'] = self.account
        try: 
            super().render('./template/'+templ, **kwargs)
        except Exception as e:
            if config.TORNADO_SETTING['debug_mode']:
                kwargs['err'] = str(e)
            else:
                kwargs['err'] = ''
            self.set_status(500)
            super().render('./template/err/err.html', **kwargs)


    @tornado.gen.coroutine
    def prepare(self):
        self.title = 'Title'
        res = yield super().prepare()
        msg = yield self.check_permission()
        if isinstance(msg, tuple):
            ### if not login give it a try
            if self.account['isLOGIN']:
                self.write_error(msg)
            else:
                self.redirect("/users/signin/?next_url=%s"%quote(self.request.uri, safe=''))

class StaticFileHandler(tornado.web.StaticFileHandler, RequestHandler):
    @tornado.gen.coroutine
    def prepare(self):
        yield super().prepare()
        msg = yield self.check_permission()
        if isinstance(msg, tuple):
            self.set_status(msg[0])
            self.finish()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
