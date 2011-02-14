#coding=utf-8

# Django settings for hchq 
import os
# hack to accommodate Windows
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).decode('utf-8')).replace('\\', '/')
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Bright Pan', 'loststriker@gmail.com'),
)
MANAGERS = (
    ('Bright Pan', 'loststriker@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%s/hckq.database' % CURRENT_PATH,                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#DATABASES = {
#    'default': {
#        'ENGINE': 'sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'e:/hchq.database',                      # Or path to database file if using sqlite3.
#        'USER': '',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#    }
#}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

SITE_NAME = '江西省会昌县计生委考勤管理系统'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(CURRENT_PATH, 'static/').replace('\\', '/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q%+l+p2fn%04(f@!_afovei3*8f)4m9_hk=5i_j*c1dn0sa3dm'

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
)

ROOT_URLCONF = 'hchq.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(CURRENT_PATH, 'templates/').replace('\\', '/'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
#    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'hchq.untils.context_processors.hchq',
)
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
CACHE_BACKEND = 'locmem://'
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
#CACHE_BACKEND = 'caching.backends.memcached://localhost:11211'
#CACHE_MIDDLEWARE_KEY_PREFIX = ''
#CACHE_MIDDLEWARE_SECONDS = 600
#CACHE_COUNT_TIMEOUT = 60  # seconds, not too long.

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # 'djangodblog',

    # django-sentry app
#    'sentry',
#    'sentry.client',
#    'paging',
#    'indexer',
#    'sentry.plugins.sentry_servers',
#    'sentry.plugins.sentry_sites',
#    'sentry.plugins.sentry_urls',

    # local app
    'hchq.untils',
    'hchq.department',
    'hchq.check_project',
    'hchq.check_object',
    'hchq.check_result',
)

AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_URL = '/account/login'

MAX_PHOTO_UPLOAD_SIZE = 1024 * 1024

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
