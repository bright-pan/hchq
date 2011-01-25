#% -*- coding: utf-8 -*-
#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q

from hchq.check_project.models import CheckProject
from hchq.service_area.models import ServiceArea
from hchq.report.check_project_report import check_project_report

@csrf_protect
@login_required
@permission_required('department.cr_report')
def report_statistics(request, template_name='my.html', next='/', ):
    """
    检查项目数据统计
    """
    try:
        check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    except ObjectDoesNotExist:
        return check_project_report()
    query_set = ServiceArea.objects.filter(is_active=True).order_by('id')
    return check_project_report(query_set, request)

@csrf_protect
@login_required
@permission_required('department.cr_report')
def report_check_or_not(request, template_name='my.html', next='/', ):
    """
    检查项目数据统计
    """
    try:
        check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    except ObjectDoesNotExist:
        return check_project_report()
    query_set = ServiceArea.objects.filter(is_active=True).order_by('id')
    return check_project_report(query_set, request)
