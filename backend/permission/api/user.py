from req import Service
from permission.base import BasePermission


class UserSignUp(BasePermission):
    def post(self, req):
        pass

class UserSignIn(BasePermission):
    def post(self, req):
        if len(req.account):
            return (401, "You have already signined.")

