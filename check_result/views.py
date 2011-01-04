#coding=utf-8
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from hchq.check_result.forms import *
from hchq.check_object.forms import *
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings

# Create your views here.
def check_result_modify(request, template_name='my.html', next='/', check_result_page='1'):
    raise Http404('Invalid Request!')
def check_result_add_uploader(request, template_name='my.html', next='/', check_result_page='1'):
    raise Http404('Invalid Request!')
def check_result_detail_modify_uploader(request, template_name='my.html', next='/', check_result_page='1'):
    raise Http404('Invalid Request!')
    
@csrf_protect
@login_required
def check_result_show(request, template_name='', next='', check_result_index='1'):
    """
    检查结果详细信息显示。
    """
    page_title=u'检查结果详情'

    if request.method == 'POST':
        raise Http404('Invalid Request!')
            
    else:
        try:
            check_result_id = int(check_result_index)
        except ValueError:
            raise Http404('Invalid Request!')
        try:
            result = CheckResult.objects.get(pk=check_result_id, is_active=True)
        except ObjectDoesNotExist:
            raise Http404('Invalid Request!')
        
    return render_to_response(template_name,
                              {'result': result,
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
def check_result_add(request, template_name='my.html', next_template_name='my.html', check_object_page='1',):
    """
    检查结果修改视图
    """
    user = get_user(request)
    
    page_title = u'选择检查对象'
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'检查':
            check_result_add_form = CheckResultAddForm(post_data)
            if check_result_add_form.is_valid():

                check_result_add_object = check_result_add_form.object()
                print check_result_add_object.id
#                print check_result_add_object.id_number
                check_result_detail_add_form = CheckResultDetailAddForm()
                check_result_detail_add_form.init_value(user, check_result_add_object)
#                print '************************8'
                page_title = u'添加检查结果'
                return render_to_response(next_template_name,
                                          {'detail_add_form': check_result_detail_add_form,
                                           'result': check_result_add_object,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
            else:
                raise Http404('Invalid Request!')
        else:
            if submit_value == u'查询':
                check_object_search_form = CheckObjectSearchForm(post_data)
                check_result_add_form = CheckResultAddForm()
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
                else:
                    results_page = None
                return render_to_response(template_name,
                                          {'search_form': check_object_search_form,
                                           'add_form': check_result_add_form,
                                           'page_title': page_title,
                                           'results_page':results_page,
                                           },
                                          context_instance=RequestContext(request))

            else:
                raise Http404('Invalid Request!')
    else:
        check_result_add_form = CheckResultAddForm()
        check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'add_form': check_result_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
def check_result_detail_add(request, template_name='my.html', next='/', check_result_page='1',):
    """
    检查结果修改视图
    """

    page_title = u'编辑检查结果'
    user = get_user(request)
    if request.method == 'GET':
        post_data = request.GET.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'确定':
            check_result_id = int(post_data['id'])
            check_result_object = CheckObject.objects.get(pk=check_result_id)
            check_result_detail_add_form = CheckResultDetailAddForm(post_data)
            check_result_detail_add_form.init_value(user, check_result_object)
            if check_result_detail_add_form.is_valid():
                check_result_detail_add_form.detail_add(user)
                return HttpResponseRedirect(next)
            else:
                return render_to_response(template_name,
                                          {'detail_add_form': check_result_detail_add_form,
                                           'result': check_result_object,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))

        else:
            raise Http404('Invalid Request!')
    else:
        raise Http404('Invalid Request!')

@csrf_protect
@login_required
def check_result_delete(request, template_name='my.html', next='/', check_result_page='1',):
    """
    检查结果删除视图
    """

    raise Http404('Invalid Request!')                


@csrf_protect
@login_required
def check_result_list(request, template_name='my.html', next='/', check_result_page='1',):
    """
    检查结果查询视图
    """
    page_title = u'查询检查结果'

    if request.method == 'POST':
        post_data = request.POST.copy()
        check_object_search_form = CheckResultSearchForm(post_data)
        if check_object_search_form.is_valid():
            check_object_search_form.data_to_session(request)
            check_object_search_form.init_from_session(request)
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_result_page, query_set, settings.CHECK_RESULT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_object_search_form = CheckResultSearchForm(CheckResultSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_result_page, query_set, settings.CHECK_RESULT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    
