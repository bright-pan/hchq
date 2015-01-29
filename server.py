#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
from gevent import wsgi
from hchq.wsgi import application
HOST = '127.0.0.1'
PORT = 8088
# set spawn=None for memcache
wsgi.WSGIServer((HOST, PORT), application).serve_forever()