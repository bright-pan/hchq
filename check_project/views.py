#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q

from hchq.check_project.forms import CheckProjectAddForm, CheckProjectModifyForm, CheckProjectDeleteForm, CheckProjectSearchForm
from hchq.check_project.models import CheckProject
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings


@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def check_project_add(request, template_name='my.html', next='/', check_project_page='1'):
    """
    检查项目添加视图，带添加预览功能！
    """
    page_title = u'添加检查项目'
    user = get_user(request)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加':
            check_project_add_form = CheckProjectAddForm(post_data)
            if check_project_add_form.is_valid():
                check_project_add_form.check_project_add(user)
            else:
                pass
            data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                    'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                    }
#            print data['check_project_name']
#            print data['is_fuzzy']
            check_project_search_form = CheckProjectSearchForm(data)
            if check_project_search_form.is_valid():
                if check_project_search_form.is_null() is False:
                    if check_project_search_form.fuzzy_search() is False:
                        query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                    else:
                        check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    query_set = CheckProject.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            check_project_add_form = CheckProjectAddForm()
            if submit_value == u'查询':
                check_project_search_form = CheckProjectSearchForm(post_data)
                if check_project_search_form.is_valid():
                    check_project_search_form.save_to_session(request)
                    if check_project_search_form.is_null() is False:
                        if check_project_search_form.fuzzy_search() is False:
                            query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                        else:
                            check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
                    else:
                        query_set = CheckProject.objects.filter(Q(is_active = True))

                else:
#                    query_set = Check_Project.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'add_form': check_project_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_project_add_form = CheckProjectAddForm()
        data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                }
        check_project_search_form = CheckProjectSearchForm(data)
        if check_project_search_form.is_valid():
            if check_project_search_form.is_null() is False:
                if check_project_search_form.fuzzy_search() is False:
                    query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
            else:
                query_set = CheckProject.objects.filter(Q(is_active = True))

        else:
            query_set = CheckProject.objects.filter(Q(is_active = True))
        results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'add_form': check_project_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def check_project_show(request, template_name='', next='', check_project_index='1'):
    """
    检查项目详细信息显示。
    """
    page_title=u'检查项目详情'
    try:
        check_project_id = int(check_project_index)
    except ValueError:
        check_project_id = 1
    try:
        result = CheckProject.objects.get(pk=check_project_id)
    except ObjectDoesNotExist:
        result = None
    return render_to_response(template_name,
                              {'result': result
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def check_project_modify(request, template_name='my.html', next='/', check_project_page='1',):
    """
    服务区修改视图
    """
    page_title = u'修改检查项目'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'修改':
            check_project_modify_form = CheckProjectModifyForm(post_data)
            if check_project_modify_form.is_valid():
                check_project_modify_object = check_project_modify_form.check_project_object()
                check_project_detail_modify_form = CheckProjectModifyForm()
                return render_to_response(next,
                                          {'modify_form': check_project_detail_modify_form,
                                           'object': check_project_modify_object,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
            else:
                pass
            data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                    'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                    }
            check_project_search_form = CheckProjectSearchForm(data)
            if check_project_search_form.is_valid():
                if check_project_search_form.is_null() is False:
                    if check_project_search_form.fuzzy_search() is False:
                        query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                    else:
                        check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    query_set = CheckProject.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            check_project_modify_form = CheckProjectModifyForm()
            if submit_value == u'查询':
                check_project_search_form = CheckProjectSearchForm(post_data)
                if check_project_search_form.is_valid():
                    check_project_search_form.save_to_session(request)
                    if check_project_search_form.is_null() is False:
                        if check_project_search_form.fuzzy_search() is False:
                            query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                        else:
                            check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
                    else:
                        query_set = CheckProject.objects.filter(Q(is_active = True))

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'modify_form': check_project_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_project_modify_form = CheckProjectModifyForm()
        data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                }        
        check_project_search_form = CheckProjectSearchForm(data)
        if check_project_search_form.is_valid():
            if check_project_search_form.is_null() is False:
                if check_project_search_form.fuzzy_search() is False:
                    query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
            else:
                query_set = CheckProject.objects.filter(Q(is_active = True))

        else:
            query_set = CheckProject.objects.filter(Q(is_active = True))
        results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'modify_form': check_project_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def check_project_delete(request, template_name='my.html', next='/', check_project_page='1',):
    """
    检查项目删除视图
    """
    page_title = u'删除检查项目'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'删除':
            check_project_delete_form = CheckProjectDeleteForm(post_data)
            if check_project_delete_form.is_valid():
                check_project_delete_form.check_project_delete()
            else:
                pass
            data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                    'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                    }        
            check_project_search_form = CheckProjectSearchForm(data)
            if check_project_search_form.is_valid():
                if check_project_search_form.is_null() is False:
                    if check_project_search_form.fuzzy_search() is False:
                        query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                    else:
                        check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    query_set = CheckProject.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            check_project_delete_form = CheckProjectDeleteForm()
            if submit_value == u'查询':
                check_project_search_form = CheckProjectSearchForm(post_data)
                if check_project_search_form.is_valid():
                    check_project_search_form.save_to_session(request)
                    if check_project_search_form.is_null() is False:
                        if check_project_search_form.fuzzy_search() is False:
                            query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                        else:
                            check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
                    else:
                        query_set = CheckProject.objects.filter(Q(is_active = True))

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'delete_form': check_project_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_project_delete_form = CheckProjectDeleteForm()
        data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                }        
        check_project_search_form = CheckProjectSearchForm(data)
        if check_project_search_form.is_valid():
            if check_project_search_form.is_null() is False:
                if check_project_search_form.fuzzy_search() is False:
                    query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
            else:
                query_set = CheckProject.objects.filter(Q(is_active = True))

        else:
            query_set = CheckProject.objects.filter(Q(is_active = True))
        results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'delete_form': check_project_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

    
@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def check_project_list(request, template_name='my.html', next='/', check_project_page='1',):
    """
    检查项目查询视图
    """
    page_title = u'查询检查项目'

    if request.method == 'POST':
        post_data = request.POST.copy()
        check_project_search_form = CheckProjectSearchForm(post_data)
        if check_project_search_form.is_valid():
            check_project_search_form.save_to_session(request)
            if check_project_search_form.is_null() is False:
                if check_project_search_form.fuzzy_search() is False:
                    query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                else:
                    check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
            else:
                query_set = CheckProject.objects.filter(Q(is_active = True))

        else:
            query_set = None
        if query_set is not None:
            results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        data = {'check_project_name':request.session.get(gl.session_check_project_name, u''),
                'is_fuzzy':request.session.get(gl.session_check_project_is_fuzzy, False),
                }        
#       print data['is_fuzzy']

        check_project_search_form = CheckProjectSearchForm(data)
        if check_project_search_form.is_valid():
            if check_project_search_form.is_null() is False:
                if check_project_search_form.fuzzy_search() is False:
                    query_set = CheckProject.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=check_project_search_form.cleaned_data['check_project_name']))
                else:
#                    print '********'
                    check_project_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = CheckProject.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=check_project_search_form.cleaned_data['check_project_name']))
            else:
                query_set = CheckProject.objects.filter(Q(is_active = True))

        else:
            query_set = CheckProject.objects.filter(Q(is_active = True))
        results_page = pagination_results(check_project_page, query_set, settings.CHECK_PROJECT_PER_PAGE)
        return render_to_response(template_name,
                                  {'search_form': check_project_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))