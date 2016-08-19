import tornado
import tornado.gen

from req import Service
from req import ApiRequestHandler

class UserSignUp(ApiRequestHandler):
    @tornado.gen.coroutine
    def post(self):
        args = ['account', 'email', 'password', 'repassword']
        data = self.get_args(args)
        err, res = yield from Service.User.post_user(data)
        if err: self.render(err)
        else: self.render(res)

class UserSignIn(ApiRequestHandler):
    @tornado.gen.coroutine
    def post(self):
        args = ['account', 'password']
        data = self.get_args(args)
        err, res = yield from Service.User.signin_by_password(self, data)
        if err: self.render(err)
        else: self.render(res)

class UserSignOut(ApiRequestHandler):
    @tornado.gen.coroutine
    def post(self):
        Service.User.signout(self)
        self.render()
