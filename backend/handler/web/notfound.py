import tornado
import tornado.gen

from req import Service
from req import WebRequestHandler

class NotFound(WebRequestHandler):
    @tornado.gen.coroutine
    def get(self, path):
        self.render('err/404.html', path=path)
