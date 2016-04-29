from copy import copy
import logging

class BaseService:
    def __init__(self, db, rs):
        self.db = db
        self.rs = rs

    def log(self, msg):
        class_name = self.__class__.__name__
        caller_function = inspect.stack()[1].function
        caller_lineno = inspect.stack()[1].lineno
        caller_filename = inspect.stack()[1].filename
        msg = '<%s@%s@%s@%s> %s' % (caller_filename, caller_lineno, self.__class__.__name__, caller_function, str(msg))
        logging.debug(msg)

    def check_required_args(self, args, data):
        for a in args:
            if a not in data:
                return 'Error: %s should exist' % a
            if data[a] is None:
                return 'Error: %s should not be None.' % a
        return None

    def gen_insert_sql(self, tablename, _data):
        data = copy(_data)
        for col in _data:
            if _data[col] is None:
                del data[col]
        sql1 = ''.join( ' "%s",'%col for col in data )[:-1]
        sql2 = (' %s,'*len(data))[:-1]
        prama = tuple( val for val in data.values() )
        sql = 'INSERT INTO "%s" (%s) VALUES(%s) RETURNING id;' % (tablename, sql1, sql2)
        return (sql, prama)
    
    def gen_update_sql(self, tablename, _data):
        data = copy(_data)
        for col in _data:
            if _data[col] is None:
                del data[col]
        sql = ''.join(' "%s" = %%s,'%col for col in data)[:-1]
        prama = tuple( val for val in data.values() )
        sql = 'UPDATE "%s" SET %s '%(tablename, sql)
        return (sql, prama)

    def gen_select_sql(self, tablename, data):
        sql = ''.join(' "%s",'%col for col in data)[:-1]
        sql = 'SELECT %s FROM "%s" '%(sql, tablename)
        return sql
