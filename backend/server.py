import tornado
import tornado.web
import tornado.netutil
import tornado.httpserver

import time
import signal
import config


def sig_handler(sig, frame):
    print('Catch Stop Signal')
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
    print('Server Stopping')
    global srv
    srv.stop()
    io_loop = tornado.ioloop.IOLoop.instance()
    deadline = time.time() + config.MAX_WAIT_SECOND_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            print('Server Stopped')
    stop_loop()

if __name__ == '__main__':
    print('Server Starting')
    if not config.TORNADO_SETTING['debug']:
        sock = tornado.netutil.bind_sockets(config.PORT)
        tornado.process.fork_processes(config.TORNADO_SETTING['processes'])

    ##################################################
    ### Setting Service                            ###
    ##################################################
    from req import Service__init__
    Service__init__()

    ##################################################
    ### Setting url                                ###
    ##################################################
    from urls import urls
    app = tornado.web.Application(urls, ** config.TORNADO_SETTING)

    global srv
    srv = tornado.httpserver.HTTPServer(app)
    if not config.TORNADO_SETTING['debug']:
        srv.add_sockets(sock)
    else:
        srv.listen(config.PORT)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    print('Server Started')
    tornado.ioloop.IOLoop().instance().start()
