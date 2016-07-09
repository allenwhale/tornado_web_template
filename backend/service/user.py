from req import Service
import config
import hashlib
import csv
import io
import time
import os
import shutil
import zipfile
from service.base import BaseService

def HashPassword(x):
    hpwd = hashlib.sha512(str(x).encode()).hexdigest() + config.TORNADO_SETTING['password_salt']
    hpwd = hashlib.md5(str(hpwd).encode()).hexdigest()
    return str(hpwd)

def GenToken(account):
    token = []
    token.append(config.TOKEN['prefix'])
    token.append(hashlib.md5(account['account'].encode()).hexdigest()[:10])
    token.append(hashlib.md5((account['password'] + str(time.time())).encode()).hexdigest()[:40])
    return '@'.join(token)


class User(BaseService):
    def post_user(self, data={}):
        required_args = [{
            'name': '+account',
            'type': str,
        }, {
            'name': '+password',
            'type': str,
        }, {
            'name': '+repassword',
            'type': str,
        }, {
            'name': '+email',
            'type': str,
        },]
        err = self.form_validation(data, required_args)
        if err: return (err, None)
        ### check email
        ### check password = repassword
        if data['password'] != data['repassword']:
            return ((400, "password is not equal to repassword"), None)
        data.pop('repassword')
        ### set token
        data['token'] = GenToken(data)
        data['password'] = HashPassword(data['password'])
        sql, param = self.gen_insert_sql('users', data)

        res = yield self.db.execute(sql, param)
        res = res.fetchone()
        if res is None:
            return ((404, "User Not Exist"), None)
        return (None, res)

    def signin_by_password(self, req, data={}):
        required_args = [{
            'name': '+account',
            'type': str,
        }, {
            'name': '+password',
            'type': str,
        },]
        err = self.form_validation(data, required_args)
        if err: return (err, None)
        res = yield self.db.execute("SELECT * FROM users WHERE account=%s", (data['account'], ))
        res = res.fetchone()
        if res is None:
            return ((404, "User Not Exist"), None)
        if res['password'] != HashPassword(data['password']):
            return ((403, "Wrong Password"), None)
        res.pop('password')
        req.set_secure_cookie('token', res['token'])
        return (None, res)

    def signin_by_token(self, req, data={}):
        required_args = [{
            'name': '+token',
            'type': str,
        },]
        err = self.form_validation(data, required_args)
        if err: return (err, None)
        res = yield self.db.execute("SELECT * FROM users WHERE token=%s", (data['token'],))
        res = res.fetchone()
        if res is None:
            return ((404, 'User Not Exist'), None)
        res.pop('password')
        req.set_secure_cookie('token', res['token'])
        return (None, res)

