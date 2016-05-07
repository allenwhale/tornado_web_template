import psycopg2
import psycopg2.extras

MAX_WAIT_SECOND_BEFORE_SHUTDOWN = 3
PORT = 3011

TORNADO_SETTING = {}
TORNADO_SETTING['debug'] = True
TORNADO_SETTING['cookie_secret'] = 'cookie secret!'
TORNADO_SETTING['compress_response'] = True
TORNADO_SETTING['autoescape'] = 'xhtml_escape'
TORNADO_SETTING['xheaders'] = True

DB_SETTING = {}
DB_SETTING['dsn'] = 'dbname=nctuoj_contest user=nctuoj_contest password=nctuoj_contest host=localhost port=5432'
DB_SETTING['size'] = 1
DB_SETTING['max_size'] = 10
DB_SETTING['setsession'] = ("SET TIME ZONE +8",)
DB_SETTING['raise_connect_errors'] = False
DB_SETTING['cursor_factory'] = psycopg2.extras.RealDictCursor

REDIS_SETTING = {}
REDIS_SETTING['host'] = 'localhost'
REDIS_SETTING['port'] = 6379
REDIS_SETTING['db'] = 1
REDIS_SETTING['data_expire_second'] = 3600
