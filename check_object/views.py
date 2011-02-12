#coding=utf-8
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from hchq.check_object.forms import *
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings
from hchq.report.check_object_report import check_object_report
# Create your views here.
@csrf_protect
@login_required
def check_object_add(request, template_name='my.html', next='/', check_object_page='1'):
    """
    考勤对象添加视图，带添加预览功能！
    """
    page_title = u'添加考勤对象'
    user = get_user(request)

    if request.method == 'GET':
        post_data = request.GET.copy()
        submit_value = post_data.get(u'submit', u'')
        if submit_value == u'添加':
            check_object_add_form = CheckObjectAddForm(post_data)
            if check_object_add_form.is_valid():
                check_object = check_object_add_form.add(user)
                if check_object is not None:
                    return HttpResponseRedirect("check_object/show/%s" % check_object.id)
                else:
                    raise Http404('Invalid Request!')
            else:
                return render_to_response(template_name,
                                          {'add_form': check_object_add_form,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))

        else:
            check_object_add_form = CheckObjectAddForm()
            return render_to_response(template_name,
                                      {'add_form': check_object_add_form,
                                       'page_title': page_title,
                                       },
                                      context_instance=RequestContext(request))
    else:
        raise Http404('Invalid Request!')
    
    
@csrf_protect
@login_required
def check_object_show(request, template_name='', next='', check_object_index='1'):
    """
    考勤对象详细信息显示。
    """
    page_title=u'考勤对象详情'

    if request.method == 'POST':
        raise Http404('Invalid Request!')
            
    else:
        try:
            check_object_id = int(check_object_index)
        except ValueError:
            raise Http404('Invalid Request!')
        try:
            result = CheckObject.objects.get(pk=check_object_id, is_active=True)
        except ObjectDoesNotExist:
            raise Http404('Invalid Request!')
        
    return render_to_response(template_name,
                              {'result': result,
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
def check_object_modify(request, template_name='my.html', next_template_name='my.html', check_object_page='1',):
    """
    考勤对象修改视图
    """
    page_title = u'编辑考勤对象'
    user = get_user(request)
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'编辑':
            check_object_modify_form = CheckObjectModifyForm(post_data)
            if check_object_modify_form.is_valid():
                check_object_modify_object = check_object_modify_form.object()
#                print check_object_modify_object.id_number
                check_object_detail_modify_form = CheckObjectDetailModifyForm(CheckObjectDetailModifyForm().data_from_object(check_object_modify_object, user))
                if check_object_detail_modify_form.is_valid():
                    check_object_detail_modify_form.init_from_object(check_object_modify_object, user)
                    page_title = u'修改考勤对象'
                    return render_to_response(next_template_name,
                                              {'detail_modify_form': check_object_detail_modify_form,
                                               'check_object': check_object_modify_object,
                                               'page_title': page_title,
                                               },
                                              context_instance=RequestContext(request))
                else:
                    raise Http404('Invalid Request!')                
            else:
                pass
            check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
            check_object_search_form.init_from_session(request)
            if check_object_search_form.is_valid():
                query_set = check_object_search_form.search()
                results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
            else:
                results_page = None
        else:
            if submit_value == u'查询':
                check_object_search_form = CheckObjectSearchForm(post_data)
                check_object_modify_form = CheckObjectModifyForm()
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
                else:
                    results_page = None
            else:
                raise Http404('Invalid Request!')                
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'modify_form': check_object_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_object_modify_form = CheckObjectModifyForm()
        check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'modify_form': check_object_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
def check_object_detail_modify(request, template_name='my.html', next='/', check_object_page='1',):
    """
    考勤对象修改视图
    """

    page_title = u'编辑考勤对象'
    
    if request.method == 'GET':
        post_data = request.GET.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'修改':
            check_object_detail_modify_form = CheckObjectDetailModifyForm(post_data)

            if check_object_detail_modify_form.is_valid():
                check_object = check_object_detail_modify_form.detail_modify(request)
                if check_object is not None:
                    return HttpResponseRedirect("check_object/show/%s" % check_object.id)
                else:
                    raise Http404('Invalid Request!')
            else:
                check_object_id = int(check_object_detail_modify_form.data.get('id'))
                check_object_object = CheckObject.objects.get(pk=check_object_id)
                return render_to_response(template_name,
                                          {'detail_modify_form': check_object_detail_modify_form,
                                           'check_object': check_object_object,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))

        else:
            raise Http404('Invalid Request!')
    else:
        raise Http404('Invalid Request!')

@csrf_protect
@login_required
def check_object_delete(request, template_name='my.html', next='/', check_object_page='1',):
    """
    考勤对象删除视图
    """
    page_title = u'删除考勤对象'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'删除':
            check_object_delete_form = CheckObjectDeleteForm(post_data)
            if check_object_delete_form.is_valid():
                check_object_delete_form.delete()
            else:
                pass
            check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
            check_object_search_form.init_from_session(request)
            if check_object_search_form.is_valid():
                query_set = check_object_search_form.search()
                results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
            else:
                results_page = None
        else:
            if submit_value == u'查询':
                check_object_search_form = CheckObjectSearchForm(post_data)
                check_object_delete_form = CheckObjectDeleteForm()
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
                else:
                    results_page = None
            else:
                raise Http404('Invalid Request!')                
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'delete_form': check_object_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_object_delete_form = CheckObjectDeleteForm()
        check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'delete_form': check_object_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


@csrf_protect
@login_required
def check_object_list(request, template_name='my.html', next='/', check_object_page='1',):
    """
    考勤对象查询视图
    """
    page_title = u'查询考勤对象'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', u'')
        if submit_value == u'查询':
            check_object_search_form = CheckObjectSearchForm(post_data)
            if check_object_search_form.is_valid():
                check_object_search_form.data_to_session(request)
                check_object_search_form.init_from_session(request)
                query_set = check_object_search_form.search()
                results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
            else:
                results_page = None
            return render_to_response(template_name,
                                      {'search_form': check_object_search_form,
                                       'page_title': page_title,
                                       'results_page': results_page,
                                       },
                                      context_instance=RequestContext(request))
        else:
            if submit_value == u'打印考勤对象报表':
                check_object_search_form = CheckObjectSearchForm(post_data)
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    return check_object_report(query_set, request)
                else:
                    results_page = None
                    return render_to_response(template_name,
                                              {'search_form': check_object_search_form,
                                               'page_title': page_title,
                                               'results_page': results_page,
                                               },
                                              context_instance=RequestContext(request))
            else:
                raise Http404('Invalid Request!')                
    else:
        check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    
