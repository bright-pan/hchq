#coding=utf-8

from hchq import settings
from hchq.check_project.models import *
from django.db.models import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

def hchq(request):
    try:
        try:
            check_project = CheckProject.objects.get(is_setup=True, is_active=True)
        except MultipleObjectsReturned:
            CheckProject.objects.filter(is_setup=True).update(is_setup=False)         
            check_project_latest = CheckProject.objects.latest('created_at')
            check_project_latest.is_setup = True
            check_project_latest.save()
    except ObjectDoesNotExist:
        check_project = None
    return {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
        'check_project': check_project,
        }
