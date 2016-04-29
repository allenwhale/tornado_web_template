import json
import logging
import datetime
import tornado.template
import tornado.gen
import tornado.web
import tornado.websocket
import datetime
import inspect
from urllib.parse import quote

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

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def log(self, msg):
        class_name = self.__class__.__name__
        caller_function = inspect.stack()[1].function
        caller_lineno = inspect.stack()[1].lineno
        caller_filename = inspect.stack()[1].filename
        msg = '<%s@%s@%s@%s> %s' % (caller_filename, caller_lineno, self.__class__.__name__, caller_function, str(msg))
        logging.debug(msg)

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

    def prepare(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        self.remote_ip = remote_ip
        print("[%s] %s %s"%(self.request.method, self.request.uri, self.remote_ip))




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

    def prepare(self):
        super().prepare()

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

    def prepare(self):
        super().prepare()

class StaticFileHandler(tornado.web.StaticFileHandler):
    def prepare(self):
        super().prepare()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

