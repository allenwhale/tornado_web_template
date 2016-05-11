import json
import datetime
import tornado.template
import tornado.gen
import tornado.web
import tornado.websocket
import datetime
import inspect
from urllib.parse import quote
from log import log
import momoko
import config
import types
import re
from utils.form import form_validation
from utils.utils import *
from include import *

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class Service:
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
    include(Service, "./service", ["base.py"], True)
    Service.Permission = T()
    include(Service.Permission, "./permission/", ["base.py"], True)

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
        path, module = get_module_path(self)
        path = path.split(".")[:-1]
        cls = Service.Permission
        for directory in path:
            if hasattr(cls, directory):
                cls = getattr(cls, directory)
            else:
                return None
        if hasattr(cls, module):
            cls = getattr(cls, module)
        else:
            return None

        if hasattr(cls, self.request.method.lower()):
            res = getattr(cls, self.request.method.lower())(self)
        else:
            return None

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
        print("[%s] %s %s"%(self.request.method, self.request.uri, self.remote_ip))
        ##################################################
        ### Get Identity                               ###
        ##################################################
        ### API Using token
        ### Web Using cookie
        ##################################################
        ### Get Basic Information                      ###
        ##################################################
        
        ##################################################
        ### Check Permission                           ###
        ##################################################
        err = yield self.check_permission()
        if err:
            self.write_error((403, err))
        


class ApiRequestHandler(RequestHandler):
    def render(self, msg=""):
        if isinstance(msg, tuple): code, msg = msg
        else: code = 200
        self.set_status(code)
        self.finish(json.dumps({
                'msg': msg
            },
            cls=DatetimeEncoder))

    def write_error(self, err, **kwargs):
        self.render(err)

    @tornado.gen.coroutine
    def prepare(self):
        res = yield super().prepare()

class WebRequestHandler(RequestHandler):
    def set_secure_cookie(self, name, value, expires_days=30, version=None, **kwargs):
        kwargs['httponly'] = True
        super().set_secure_cookie(name, value, expires_days, version, **kwargs)

    def write_error(self, err, **kwargs):
        try: status_code, err = err
        except: status_code = err; err = ''
        kwargs['err'] = err
        self.set_status(status_code)
        self.render('./err/'+str(status_code)+'.html', **kwargs)

    def render(self, templ, **kwargs):
        super().render('./web/template/'+templ, **kwargs)

    @tornado.gen.coroutine
    def prepare(self):
        res = yield super().prepare()

class StaticFileHandler(tornado.web.StaticFileHandler):
    def prepare(self):
        super().prepare()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

