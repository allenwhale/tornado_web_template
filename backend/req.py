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
from utils.form import form_validation

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
    from service.simple import SimpleService
    Service.Simple = SimpleService()

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


class ApiRequestHandler(RequestHandler):
    def render(self, msg=""):
        if isinstance(msg, tuple): code, msg = msg
        else: code = 200
        self.set_status(code)
        self.finish(json.dumps({
                'msg': msg
            },
            cls=DatetimeEncoder))
        return

    @tornado.gen.coroutine
    def prepare(self):
        yield super().prepare()

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
        yield super().prepare()

class StaticFileHandler(tornado.web.StaticFileHandler):
    def prepare(self):
        super().prepare()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

