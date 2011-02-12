#coding=utf-8

from hchq import settings

def hchq(request):
    return {
        'site_name': settings.SITE_NAME,
        }
