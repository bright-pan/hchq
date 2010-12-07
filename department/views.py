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

from hchq.department.forms import DepartmentAddForm, DepartmentModifyForm, DepartmentDeleteForm, DepartmentSearchForm
from hchq.department.models import Department
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings


@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def department_add(request, template_name='my.html', next='/', department_page='1'):
    """
    部门单位添加视图，带添加预览功能！
    """
    page_title = u'添加部门单位'
    user = get_user(request)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加':
            department_add_form = DepartmentAddForm(post_data)
            if department_add_form.is_valid():
                department_add_form.department_add(user)
            else:
                pass
            data = {'department_name':request.session.get(gl.session_department_name, u''),
                    'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                    }
#            print data['department_name']
#            print data['is_fuzzy']
            department_search_form = DepartmentSearchForm(data)
            if department_search_form.is_valid():
                if department_search_form.is_null() is False:
                    if department_search_form.fuzzy_search() is False:
                        query_set = Department.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=department_search_form.cleaned_data['department_name']))
                    else:
                        department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = Department.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=department_search_form.cleaned_data['department_name']))
                else:
                    query_set = Department.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            department_add_form = DepartmentAddForm()
            if submit_value == u'查询':
                department_search_form = DepartmentSearchForm(post_data)
                if department_search_form.is_valid():
                    department_search_form.save_to_session(request)
                    if department_search_form.is_null() is False:
                        if department_search_form.fuzzy_search() is False:
                            query_set = Department.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=department_search_form.cleaned_data['department_name']))
                        else:
                            department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
                    else:
                        query_set = Department.objects.filter(Q(is_active = True))

                else:
#                    query_set = Department.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'add_form': department_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        department_add_form = DepartmentAddForm()
        data = {'department_name':request.session.get(gl.session_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                }
        department_search_form = DepartmentSearchForm(data)
        if department_search_form.is_valid():
            if department_search_form.is_null() is False:
                if department_search_form.fuzzy_search() is False:
                    query_set = Department.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=department_search_form.cleaned_data['department_name']))
                else:
                    department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
            else:
                query_set = Department.objects.filter(Q(is_active = True))

        else:
            query_set = Department.objects.filter(Q(is_active = True))
        results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'add_form': department_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def department_show(request, template_name='', next='', department_index='1'):
    """
    部门单位详细信息显示。
    """
    page_title=u'部门单位详情'
    try:
        department_id = int(department_index)
    except ValueError:
        department_id = 1
    try:
        result = Department.objects.get(pk=department_id)
    except ObjectDoesNotExist:
        result = None
    return render_to_response(template_name,
                              {'result': result
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def department_modify(request, template_name='my.html', next='/', department_page='1',):
    """
    服务区修改视图
    """
    page_title = u'修改部门单位'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'修改':
            department_modify_form = DepartmentModifyForm(post_data)
            if department_modify_form.is_valid():
                department_modify_form.department_modify()
            else:
                pass
            data = {'department_name':request.session.get(gl.session_department_name, u''),
                    'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                    }
            department_search_form = DepartmentSearchForm(data)
            if department_search_form.is_valid():
                if department_search_form.is_null() is False:
                    if department_search_form.fuzzy_search() is False:
                        query_set = Department.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=department_search_form.cleaned_data['department_name']))
                    else:
                        department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = Department.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=department_search_form.cleaned_data['department_name']))
                else:
                    query_set = Department.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            department_modify_form = DepartmentModifyForm()
            if submit_value == u'查询':
                department_search_form = DepartmentSearchForm(post_data)
                if department_search_form.is_valid():
                    department_search_form.save_to_session(request)
                    if department_search_form.is_null() is False:
                        if department_search_form.fuzzy_search() is False:
                            query_set = Department.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=department_search_form.cleaned_data['department_name']))
                        else:
                            department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
                    else:
                        query_set = Department.objects.filter(Q(is_active = True))

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'modify_form': department_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        department_modify_form = DepartmentModifyForm()
        data = {'department_name':request.session.get(gl.session_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                }        
        department_search_form = DepartmentSearchForm(data)
        if department_search_form.is_valid():
            if department_search_form.is_null() is False:
                if department_search_form.fuzzy_search() is False:
                    query_set = Department.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=department_search_form.cleaned_data['department_name']))
                else:
                    department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
            else:
                query_set = Department.objects.filter(Q(is_active = True))

        else:
            query_set = Department.objects.filter(Q(is_active = True))
        results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'modify_form': department_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def department_delete(request, template_name='my.html', next='/', department_page='1',):
    """
    部门单位删除视图
    """
    page_title = u'删除部门单位'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'删除':
            department_delete_form = DepartmentDeleteForm(post_data)
            if department_delete_form.is_valid():
                department_delete_form.department_delete()
            else:
                pass
            data = {'department_name':request.session.get(gl.session_department_name, u''),
                    'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                    }        
            department_search_form = DepartmentSearchForm(data)
            if department_search_form.is_valid():
                if department_search_form.is_null() is False:
                    if department_search_form.fuzzy_search() is False:
                        query_set = Department.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=department_search_form.cleaned_data['department_name']))
                    else:
                        department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = Department.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=department_search_form.cleaned_data['department_name']))
                else:
                    query_set = Department.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            department_delete_form = DepartmentDeleteForm()
            if submit_value == u'查询':
                department_search_form = DepartmentSearchForm(post_data)
                if department_search_form.is_valid():
                    department_search_form.save_to_session(request)
                    if department_search_form.is_null() is False:
                        if department_search_form.fuzzy_search() is False:
                            query_set = Department.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=department_search_form.cleaned_data['department_name']))
                        else:
                            department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
                    else:
                        query_set = Department.objects.filter(Q(is_active = True))

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'delete_form': department_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        department_delete_form = DepartmentDeleteForm()
        data = {'department_name':request.session.get(gl.session_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                }        
        department_search_form = DepartmentSearchForm(data)
        if department_search_form.is_valid():
            if department_search_form.is_null() is False:
                if department_search_form.fuzzy_search() is False:
                    query_set = Department.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=department_search_form.cleaned_data['department_name']))
                else:
                    department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
            else:
                query_set = Department.objects.filter(Q(is_active = True))

        else:
            query_set = Department.objects.filter(Q(is_active = True))
        results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'delete_form': department_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

    
@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def department_list(request, template_name='my.html', next='/', department_page='1',):
    """
    部门单位查询视图
    """
    page_title = u'查询部门单位'

    if request.method == 'POST':
        post_data = request.POST.copy()
        department_search_form = DepartmentSearchForm(post_data)
        if department_search_form.is_valid():
            department_search_form.save_to_session(request)
            if department_search_form.is_null() is False:
                if department_search_form.fuzzy_search() is False:
                    query_set = Department.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=department_search_form.cleaned_data['department_name']))
                else:
                    department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
            else:
                query_set = Department.objects.filter(Q(is_active = True))

        else:
            query_set = None
        if query_set is not None:
            results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        data = {'department_name':request.session.get(gl.session_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_department_is_fuzzy, False),
                }        
#       print data['is_fuzzy']

        department_search_form = DepartmentSearchForm(data)
        if department_search_form.is_valid():
            if department_search_form.is_null() is False:
                if department_search_form.fuzzy_search() is False:
                    query_set = Department.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=department_search_form.cleaned_data['department_name']))
                else:
#                    print '********'
                    department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Department.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=department_search_form.cleaned_data['department_name']))
            else:
                query_set = Department.objects.filter(Q(is_active = True))

        else:
            query_set = Department.objects.filter(Q(is_active = True))
        results_page = pagination_results(department_page, query_set, settings.DEPARTMENT_PER_PAGE)
        return render_to_response(template_name,
                                  {'search_form': department_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
