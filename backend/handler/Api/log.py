import tornado
import tornado.gen
from req import ApiRequestHandler


class Log(ApiRequestHandler):
    @tornado.gen.coroutine
    def post(self):
        args = ['log']
        meta = self.get_args(args)
        self.log(meta)
        self.render(meta)
