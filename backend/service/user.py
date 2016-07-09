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
    token.append(config.token['prefix'])
    token.append(hashlib.md5(account['account'].encode()).hexdigest()[:10])
    token.append(hashlib.md5((account['password'] + str(time.time())).encode()).hexdigest()[:40])
    return '@'.join(token)


class User(BaseService):
    def SignIn(self, data={}):
        required_args = [{
            'name': '+account',
            'type': str,
        }, {
            'name': '+password',
            'type': str,
        }]
        err = self.form_validation(data, required_args)
        if err: return (err, None)
        res = yield self.db.execute("SELECT * FROM users WHERE account=%s", (data['account'],))
        if res.rowcount == 0:
            return ((404, "User Not Exist"), None)
        res = res.fetchone()
        self.log(HashPassword(data['password']))
        if res['password'] != HashPassword(data['password']):
            return ((403, "Wrong Password"), None)
        err, res = yield from self.get_user_by_token(res)
        res['isLOGIN'] = True
        return (None, res)

    def get_user_by_token(self, data={}):
        required_args = [{
            'name': '+token',
            'type': str,
        },]
        err = self.form_validation(data, required_args)
        if err: return (err, None)
        res = yield self.db.execute("SELECT * FROM users WHERE token=%s", (data['token'],))
        if res.rowcount == 0:
            return ((403, 'no such user'), None)
        res = res.fetchone()
        res.pop('password')
        res['isLOGIN'] = True
        for x in map_users_type:
            res['is'+x] = 'type' in res and res['type'] == map_users_type[x]
        return (None, res)

