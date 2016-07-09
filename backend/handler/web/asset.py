import tornado
import tornado.gen

from req import Service
from req import StaticFileHandler

class Asset(StaticFileHandler):
    @tornado.gen.coroutine
    def get(self, path, include_body=True):
        self.log(path)
        yield super().get(path, include_body)
