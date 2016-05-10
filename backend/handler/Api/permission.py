import tornado
import tornado.gen
from req import ApiRequestHandler


class Permission(ApiRequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.render('access')
