#coding=utf-8
import datetime
from hchq import settings
from check_project.models import *
from django.db.models import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

def hchq(request):
    check_project = None
    check_project_time = None
    try:
        try:
            check_project = CheckProject.objects.get(is_setup=True, is_active=True)
            today = datetime.datetime.now().date()
            if check_project.start_time >= today or today >= check_project.end_time:
                check_project_time = "error"
        except MultipleObjectsReturned:
            CheckProject.objects.filter(is_setup=True).update(is_setup=False)         
            check_project = CheckProject.objects.latest('created_at')
            check_project.is_setup = True
            check_project.save()
    except ObjectDoesNotExist:
        check_project = None
    return {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
        'check_project': check_project,
        'check_project_time': check_project_time,
        }
