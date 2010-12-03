#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user

from hchq.service_area.forms import ServiceAreaAddForm
from hchq.service_area.models import ServiceArea
from hchq.untils.my_paginator import pagination_results
from hchq import settings


@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_add(request, template_name='my.html', next='/', page='1'):
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
        results_page = pagination_results(page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_add_form = ServiceAreaAddForm()
        query_set = ServiceArea.objects.filter(is_active = True)
        results_page = pagination_results(page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


