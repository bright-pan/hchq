#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q

from hchq.department.forms import DepartmentAddForm, DepartmentModifyForm, DepartmentDeleteForm, DepartmentSearchForm
from hchq.department.models import Department
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings


@csrf_protect
@login_required
@permission_required('department.sd_management')
def department_add(request, template_name='my.html', next='/', department_page='1'):
    """
    单位部门添加视图，带添加预览功能！
    """
    page_title = u'添加单位部门'
    user = get_user(request)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
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
@login_required
@permission_required('department.sd_management')
def department_show(request, template_name='', next='', department_index='1'):
    """
    单位部门详细信息显示。
    """
    page_title=u'单位部门详情'
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
@login_required
@permission_required('department.sd_management')
def department_modify(request, template_name='my.html', next='/', department_page='1',):
    """
    服务区修改视图
    """
    page_title = u'修改单位部门'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
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
@login_required
@permission_required('department.sd_management')
def department_delete(request, template_name='my.html', next='/', department_page='1',):
    """
    单位部门删除视图
    """
    page_title = u'删除单位部门'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
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
@login_required
@permission_required('department.sd_management')
def department_list(request, template_name='my.html', next='/', department_page='1',):
    """
    单位部门查询视图
    """
    page_title = u'查询单位部门'

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
@cache_page(60 * 15)
def department_name_ajax(request, template_name='my.html', next='/'):
    if request.is_ajax():
        result = []
        if request.method == 'GET':

            if request.GET.has_key('service_area_name'):
                service_area_name = request.GET['service_area_name']
#                print '***********************'
#                print type(service_area_name)
                if service_area_name == u'':
#                    print '******************8'
                    pass
                else:    
                    query_set = Department.objects.filter(is_active=True,
                                                          department_to_service_area__service_area__name=service_area_name,
                                                          department_to_service_area__is_active=True).order_by('name')
                    result = [ x.name for x in query_set]
#                    print '$$$$$$$$$$$$$'
#                    print result

            else:
                pass
        else:
            pass
        json = simplejson.dumps(result)
#        print json
        return HttpResponse(json, mimetype='application/json')
    else:
        raise Http404('Invalid Request!')
 
