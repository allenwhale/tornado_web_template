import tornado
import tornado.gen

from req import Service
from req import WebRequestHandler

class Index(WebRequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.render('index.html')
