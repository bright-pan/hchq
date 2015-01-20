#coding=utf-8

# Django settings for hchq project.
import os
# hack to accommodate Windows
CURRENT_PATH = os.path.join(os.path.dirname(__file__), '..').replace('\\', '/')
#print(CURRENT_PATH)

SITE_NAME = '江西省会昌县环情孕情管理系统'
META_KEYWORDS = '环孕检, 计生服务站, 计生委, 检查结果, 检查对象, 检查项目'
META_DESCRIPTION = '环孕检系统是会昌县计生服务站题提供的环孕检集中管理服务，用户跟踪检查对象的环孕检结果，和个人信息，并生成报表。'

ADMINS = (
    ('Bright Pan', 'loststriker@gmail.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'hchq',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'hchq2010-2014*.*',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(CURRENT_PATH, 'static/').replace('\\', '/')
#print(MEDIA_ROOT)
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(CURRENT_PATH, 'media/').replace('\\', '/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!40-1h9-z9@jg&amp;q+mc30*&amp;&amp;k6e#1*$)5s5%t!u$t*#0=l@f1=r'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'hchq.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'hchq.wsgi.application'

import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)
#print(TEMPLATE_DIRS)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
#    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'untils.context_processors.hchq',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',

    # local app
    'untils',
    'account',
    'service_area',
    'department',
    'check_project',
    'check_object',
    'check_result',
    'gunicorn',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

############
# SESSIONS #
############

SESSION_COOKIE_NAME = 'sessionid'                       # Cookie name. This can be whatever you want.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2               # Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_DOMAIN = None                            # A string like ".lawrence.com", or None for standard domain cookie.
SESSION_COOKIE_SECURE = False                           # Whether the session cookie should be secure (https:// only).
SESSION_COOKIE_PATH = '/'                               # The path of the session cookie.
SESSION_SAVE_EVERY_REQUEST = False                      # Whether to save the session data on every request.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False                 # Whether a user's session cookie expires when the Web browser is closed.
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # The module to store session data
SESSION_FILE_PATH = None                                # Directory to store session files if using the file session module. If None, the backend will use a sensible default.

#########
# CACHE #
#########

# The cache backend to use.  See the docstring in django.core.cache for the
# possible values.
#CACHE_BACKEND = 'locmem://'
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_BACKEND = 'caching.backends.memcached://localhost:11211'
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_COUNT_TIMEOUT = 60  # seconds, not too long.

AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_URL = '/account/login'

MAX_PHOTO_UPLOAD_SIZE = 1024 * 1024 * 10

SERVICE_AREA_PER_PAGE = 12
DEPARTMENT_PER_PAGE = 12
SERVICE_AREA_DEPARTMENT_PER_PAGE = 12
ROLE_PER_PAGE = 12
ROLE_PERMISSION_PER_PAGE = 12
CHECK_PROJECT_PER_PAGE = 12
ACCOUNT_PER_PAGE = 12
CHECK_OBJECT_PER_PAGE = 12
CHECK_RESULT_PER_PAGE = 12

ACCOUNT_DEFAULT_EMAIL = u'loststriker@gmail.com'
ACCOUNT_DEFAULT_PASSWORD = u'123456'

import datetime

if datetime.date.today() < datetime.date(2015, 6, 1):
    DEBUG = TEMPLATE_DEBUG = True
else:
    DEBUG = TEMPLATE_DEBUG = False


SESSION_EXPIRE_AT_BROWSER_CLOSE = True                 # Whether a user's session cookie expires when the Web browser is closed.

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'hchq2011django'
EMAIL_HOST_USER = 'hchq.django@gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
