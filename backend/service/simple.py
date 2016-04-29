from req import Service
from service.base import BaseService
from utils.form import form_validation

class SimpleService(BaseService):
    def __init__(self, db, rs):
        super().__init__(db, rs)

    def get_simple(self):
        res = yield self.db.execute('SELECT PG_SLEEP(5);')
        return (None, 'you slept five seconds')

    def post_simple(self, data={}):
        required_args = [{
            'name': '+a',
            'type': int,
        }, {
            'name': '+b',
            'type': int,
        }]
        err = form_validation(data, required_args)
        if err: return (err, None)
        res = yield self.db.execute('SELECT %s+%s AS sum;', (data['a'], data['b'], ))
        return (None, res.fetchone()['sum'])

