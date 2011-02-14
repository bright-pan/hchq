#coding=utf-8

from hchq.settings import *

DEBUG = TEMPLATE_DEBUG = False
ROOT_URLCONF = 'hchq.apache.urls_production'

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
