#coding=utf-8

from hchq import settings

def hchq(request):
    return {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
#        'request': request
        }
