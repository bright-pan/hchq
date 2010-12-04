#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist

from hchq.service_area.forms import ServiceAreaAddForm
from hchq.service_area.models import ServiceArea
from hchq.untils.my_paginator import pagination_results
from hchq import settings


@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_add(request, template_name='my.html', next='/', service_area_page='1'):
    """
    服务区添加视图，带添加预览功能！
    """
    page_title = u'添加服务区域'
    user = get_user(request)
    post_data = None

    if request.method == 'POST':
        post_data = request.POST.copy()
        service_area_add_form = ServiceAreaAddForm(post_data)
        if service_area_add_form.is_valid():
            service_area_add_form.service_area_save(user)
        query_set = ServiceArea.objects.filter(is_active = True)
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_add_form = ServiceAreaAddForm()
        query_set = ServiceArea.objects.filter(is_active = True)
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_show(request, template_name='', next='', service_area_index='1'):
    """
    服务区详细信息显示。
    """
    page_title=u'服务区域详情'
    try:
        service_area_id = int(service_area_index)
    except ValueError:
        service_area_id = 1
    try:
        result = ServiceArea.objects.get(pk=service_area_id)
    except ObjectDoesNotExist:
        result = None
    return render_to_response(template_name,
                              {'result': result
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_modify(request, template_name='my.html', next='/', service_area_page='1', service_area_index='1'):
    """
    服务区修改视图
    """
    page_title = u'添加服务区域'
    modify = None

    if request.method == 'POST':
        post_data = request.POST.copy()
        service_area_modify_form = ServiceAreaModifyForm(post_data)
        if service_area_modify_form.is_valid():
            if service_area_modify_form.service_area_save(service_area_index):
                modify = True
            else:
                modify = False
        query_set = ServiceArea.objects.filter(is_active = True)
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'form': service_area_modify_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   'modify': modify,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_modify_form = ServiceAreaModifyForm()
        query_set = ServiceArea.objects.filter(is_active = True)
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'form': service_area_modify_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   'modify': modify,
                                   },
                                  context_instance=RequestContext(request))
