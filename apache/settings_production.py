#coding=utf-8

from hchq.settings import *

DEBUG = TEMPLATE_DEBUG = False
ROOT_URLCONF = 'hchq.apache.urls_production'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True                 # Whether a user's session cookie expires when the Web browser is closed.
