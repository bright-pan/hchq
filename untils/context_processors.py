#coding=utf-8

from hchq import settings
from hchq.check_project.models import *

def hchq(request):
    try:
        check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    except ObjectDoesNotExist:
        check_project = None
    return {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
        'check_project': check_project,
        }
