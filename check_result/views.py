#coding=utf-8
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.servers.basehttp import FileWrapper

import os, tempfile, zipfile

from PIL import Image
from check_result.forms import *
from check_object.forms import *
from untils.my_paginator import pagination_results
from untils import gl, download
from hchq import settings
from report.check_result_report import check_result_report
from report.certification_report import certification_report
from report.check_object_report import *
import datetime
# Create your views here.
def check_result_modify(request, template_name='my.html', next='/', check_result_page='1'):
    raise Http404('Invalid Request!')
def check_result_add_uploader(request, template_name='my.html', next='/', check_result_page='1'):
    raise Http404('Invalid Request!')
def check_result_detail_modify_uploader(request, template_name='my.html', next='/', check_result_page='1'):
    raise Http404('Invalid Request!')

@csrf_protect
@login_required
@user_passes_test(lambda u: (u.has_perm('department.cr_list') or u.has_perm('department.cr_add')))
def check_result_show(request, template_name='', next='', next_error='my.html', check_result_index='1', success=u'false'):
    """
    检查结果详细信息显示。
    """
    page_title=u'检查结果详情'
    check_object = None
    results = None
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        try:
            check_result_id = int(check_result_index)
        except ValueError:
            raise Http404('Invalid Request!')
        try:
            check_project = CheckProject.objects.get(is_setup=True, is_active=True)
        except ObjectDoesNotExist:
            check_project = None
        try:
            check_object = CheckObject.objects.get(pk=check_result_id)
        except ObjectDoesNotExist:
            raise Http404('Invalid Request!')
        if submit_value == u'打印证明':
            qs_check_result = CheckResult.objects.filter(check_object=check_object, check_project=check_project, is_latest=True)
            if qs_check_result:
                return certification_report([check_object], request)
            else:
                success = u'invalid_result_error'
            results = CheckResult.objects.filter(check_object=check_object).order_by('-id')
        else:
            if submit_value == u'检查结果失效':
                if check_project is not None:
                    today = datetime.datetime.now().date()
                    if check_project.start_time <= today and today <= check_project.end_time:
                        qs_check_result = CheckResult.objects.filter(check_object=check_object, check_project=check_project, is_latest=True)
                        if qs_check_result:
                            check_result_object = qs_check_result[0]
                            check_result_object.result = check_result_object.result + u" invalid"
                            check_result_object.save()
                            qs_check_result.update(is_latest=False)
                            success = u'invalid_success'
                        else:
                            success = u'invalid_already'
                    else:
                        page_title = u'受限制'
                        success = u'invalid_time_error'
                else:
                    page_title = u'受限制'
                    success = u'invalid_project_error'
                results = CheckResult.objects.filter(check_object=check_object).order_by('-id')
            else:
                raise Http404('Invalid Request!')
    else:
        try:
            check_result_id = int(check_result_index)
        except ValueError:
            raise Http404('Invalid Request!')
        try:
            check_object = CheckObject.objects.get(pk=check_result_id)
        except ObjectDoesNotExist:
            #print "***************"
            raise Http404('Invalid Request!')

        results = check_object.check_result.order_by('-id')

#        print type(results[0]['is_latest'])
    return render_to_response(template_name,
                              {'results': results,
                               'check_object': check_object,
                               'success': success,
                               'page_title':page_title
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.cr_add')
def check_result_add(request, template_name='my.html', next_template_name='my.html', next_error='my.html', check_object_page='1',):
    """
    检查结果修改视图
    """
    user = get_user(request)

    page_title = u'选择检查对象'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'检查':
            try:
                check_project = CheckProject.objects.get(is_setup=True, is_active=True)
            except ObjectDoesNotExist:
                check_project = None
            if check_project is not None:
                today = datetime.datetime.now().date()
                if check_project.start_time <= today and today <= check_project.end_time:

                    check_result_add_form = CheckResultAddForm(post_data)
                    if check_result_add_form.is_valid():
                        check_result_add_object = check_result_add_form.object()
                    #                print check_result_add_object.id
                    #                print check_result_add_object.id_number
                        check_result_detail_add_form = CheckResultDetailAddForm()
                        check_result_detail_add_form.init_value(user, check_result_add_object)
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
                    page_title = u'检查受限制'
                    return render_to_response(next_error,
                                              {'check_project': check_project,
                                               'page_title': page_title,
                                               },
                                              context_instance=RequestContext(request))
            else:
                page_title = u'检查受限制'
                return render_to_response(next_error,
                                          {'check_project': check_project,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
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
                if submit_value == u'打印检查对象报表':
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
@permission_required('department.cr_add')
def check_result_detail_add(request, template_name='my.html', next='/', check_result_page='1',):
    """
    检查结果修改视图
    """

    page_title = u'编辑检查结果'
    user = get_user(request)
    if request.method == 'POST':
        #print "************************"
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'确定':
            #print "************************"
            check_result_id = int(post_data.get(u'id', False))
            check_result_object = CheckObject.objects.get(pk=check_result_id)
            check_result_detail_add_form = CheckResultDetailAddForm(post_data)
            check_result_detail_add_form.init_value(user, check_result_object)
            if check_result_detail_add_form.is_valid():

                check_result_detail_add_form.detail_add(user)
                #print "************************"
                return HttpResponseRedirect("check_result/show/%s/add/" % check_result_id)
            else:
                #print check_result_detail_add_form.errors
                #print "fffffffff************************"
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
@permission_required('department.cr_list')
def check_result_list(request, template_name='my.html', next='/', check_result_page='1',):
    """
    检查结果查询视图
    """
    page_title = u'查询检查结果'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'查询':
            check_result_search_form = CheckResultSearchForm(post_data)
            check_result_search_form.init_check_project()
            if check_result_search_form.is_valid():
                check_result_search_form.data_to_session(request)
                check_result_search_form.init_from_session(request)
                query_set = check_result_search_form.search()
                results_page = pagination_results(check_result_page, query_set, settings.CHECK_RESULT_PER_PAGE)
            else:
                results_page = None
            return render_to_response(template_name,
                                      {'search_form': check_result_search_form,
                                       'page_title': page_title,
                                       'results_page': results_page,
                                       },
                                      context_instance=RequestContext(request))
        else:
            if submit_value == u'打印检查结果报表':
                check_result_search_form = CheckResultSearchForm(post_data)
                check_result_search_form.init_check_project()
                if check_result_search_form.is_valid():
                    check_result_search_form.data_to_session(request)
                    check_result_search_form.init_from_session(request)
                    query_set = check_result_search_form.search()
                    filename = check_result_report(query_set, request)
                    #filename = '/home/bright/nanopb-0.3.1-linux-x86.tar.gz'
                    #print __file__
                    #wrapper = FileWrapper(file(filename))
                    #response = HttpResponse(wrapper, content_type='text/plain')
                    #response['Content-Length'] = os.path.getsize(filename)
                    #
                    return download.down_zipfile(request, filename)
                else:
                    results_page = None
                    return render_to_response(template_name,
                                              {'search_form': check_result_search_form,
                                               'page_title': page_title,
                                               'results_page': results_page,
                                               },
                                              context_instance=RequestContext(request))
    else:
        check_result_search_form = CheckResultSearchForm(CheckResultSearchForm().data_from_session(request))
        check_result_search_form.init_check_project()
        check_result_search_form.init_from_session(request)
        if check_result_search_form.is_valid():
            query_set = check_result_search_form.search()
            results_page = pagination_results(check_result_page, query_set, settings.CHECK_RESULT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_result_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.role_management')
def check_result_special_add(request, template_name='my.html', next_template_name='my.html', next_error='my.html', check_object_page='1',):
    """
    特殊检查结果添加视图
    """
    user = get_user(request)

    page_title = u'选择检查对象'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'特殊情况检查':
            try:
                check_project = CheckProject.objects.get(is_setup=True, is_active=True)
            except ObjectDoesNotExist:
                check_project = None
            if check_project is not None:
                today = datetime.datetime.now().date()
                if check_project.start_time <= today and today <= check_project.end_time:

                    check_result_special_add_form = CheckResultSpecialAddForm(post_data)
                    if check_result_special_add_form.is_valid():
                        check_result_special_add_object = check_result_special_add_form.object()
#                        print check_result_special_add_object
#                        print check_result_special_add_object.id_number
                        check_result_special_detail_add_form = CheckResultSpecialDetailAddForm()
                        check_result_special_detail_add_form.init_value(user, check_result_special_add_object)
                        page_title = u'添加特殊情况检查结果'
                        return render_to_response(next_template_name,
                                                  {'special_detail_add_form': check_result_special_detail_add_form,
                                                   'result': check_result_special_add_object,
                                                   'page_title': page_title,
                                                   },
                                                  context_instance=RequestContext(request))
                    else:
                        raise Http404('Invalid Request!')
                else:
                    page_title = u'检查受限制'
                    return render_to_response(next_error,
                                              {'check_project': check_project,
                                               'page_title': page_title,
                                               },
                                              context_instance=RequestContext(request))
            else:
                page_title = u'检查受限制'
                return render_to_response(next_error,
                                          {'check_project': check_project,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
        else:
            if submit_value == u'查询':
                check_object_search_form = CheckObjectSearchForm(post_data)
                check_result_special_add_form = CheckResultSpecialAddForm()
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
                else:
                    results_page = None
                return render_to_response(template_name,
                                          {'search_form': check_object_search_form,
                                           'add_form': check_result_special_add_form,
                                           'page_title': page_title,
                                           'results_page':results_page,
                                           },
                                          context_instance=RequestContext(request))

            else:
                if submit_value == u'打印检查对象报表':
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
        check_result_special_add_form = CheckResultSpecialAddForm()
        check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'add_form': check_result_special_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.role_management')
def check_result_special_detail_add(request, template_name='my.html', next='/', check_result_page='1',):
    """
    特殊检查结果添加视图
    """

    page_title = u'编辑特殊情况检查结果'
    user = get_user(request)
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'确定':
            check_result_id = int(post_data.get(u'id', False))
            check_result_object = CheckObject.objects.get(pk=check_result_id)
            check_result_special_detail_add_form = CheckResultSpecialDetailAddForm(post_data)
            check_result_special_detail_add_form.init_value(user, check_result_object)
            if check_result_special_detail_add_form.is_valid():
                check_result_special_detail_add_form.special_detail_add(user)
                return HttpResponseRedirect("check_result/show/%s/add/" % check_result_id)
            else:
                return render_to_response(template_name,
                                          {'special_detail_add_form': check_result_special_detail_add_form,
                                           'result': check_result_object,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
        else:
            raise Http404('Invalid Request!')
    else:
        raise Http404('Invalid Request!')
