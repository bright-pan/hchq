#coding=utf-8

from hchq.settings import *

DEBUG = TEMPLATE_DEBUG = False
ROOT_URLCONF = 'apache.urls_production'


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'hchq2011django'
EMAIL_HOST_USER = 'hchq.django@gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True                 # Whether a user's session cookie expires when the Web browser is closed.
