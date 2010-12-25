#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q

from hchq.service_area.forms import *
from hchq.service_area.models import ServiceArea, ServiceAreaDepartment
from hchq.department.models import Department
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings


@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_add(request, template_name='my.html', next='/', service_area_page='1'):
    """
    服务区域添加视图，带添加预览功能！
    """
    page_title = u'添加服务区域'
    user = get_user(request)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加':
            service_area_add_form = ServiceAreaAddForm(post_data)
            if service_area_add_form.is_valid():
                service_area_add_form.service_area_add(user)
            else:
                pass
            data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                    'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                    }
#            print data['service_area_name']
#            print data['is_fuzzy']
            service_area_search_form = ServiceAreaSearchForm(data)
            if service_area_search_form.is_valid():
                if service_area_search_form.is_null() is False:
                    if service_area_search_form.fuzzy_search() is False:
                        query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                    else:
                        service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    query_set = ServiceArea.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            service_area_add_form = ServiceAreaAddForm()
            if submit_value == u'查询':
                service_area_search_form = ServiceAreaSearchForm(post_data)
                if service_area_search_form.is_valid():
                    service_area_search_form.save_to_session(request)
                    if service_area_search_form.is_null() is False:
                        if service_area_search_form.fuzzy_search() is False:
                            query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                        else:
                            service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
                    else:
                        query_set = ServiceArea.objects.filter(Q(is_active = True))

                else:
#                    query_set = ServiceArea.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'add_form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_add_form = ServiceAreaAddForm()
        data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                }
        service_area_search_form = ServiceAreaSearchForm(data)
        if service_area_search_form.is_valid():
            if service_area_search_form.is_null() is False:
                if service_area_search_form.fuzzy_search() is False:
                    query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
            else:
                query_set = ServiceArea.objects.filter(Q(is_active = True))

        else:
            query_set = ServiceArea.objects.filter(Q(is_active = True))
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'add_form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_show(request, template_name='', next='', service_area_index='1'):
    """
    服务区域详细信息显示。
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
def service_area_modify(request, template_name='my.html', next='/', service_area_page='1',):
    """
    服务区域修改视图
    """
    page_title = u'修改服务区域'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'修改':
            service_area_modify_form = ServiceAreaModifyForm(post_data)
            if service_area_modify_form.is_valid():
                service_area_modify_form.service_area_modify()
            else:
                pass
            data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                    'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                    }
            service_area_search_form = ServiceAreaSearchForm(data)
            if service_area_search_form.is_valid():
                if service_area_search_form.is_null() is False:
                    if service_area_search_form.fuzzy_search() is False:
                        query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                    else:
                        service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    query_set = ServiceArea.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            service_area_modify_form = ServiceAreaModifyForm()
            if submit_value == u'查询':
                service_area_search_form = ServiceAreaSearchForm(post_data)
                if service_area_search_form.is_valid():
                    service_area_search_form.save_to_session(request)
                    if service_area_search_form.is_null() is False:
                        if service_area_search_form.fuzzy_search() is False:
                            query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                        else:
                            service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
                    else:
                        query_set = ServiceArea.objects.filter(Q(is_active = True))

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'modify_form': service_area_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_modify_form = ServiceAreaModifyForm()
        data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                }        
        service_area_search_form = ServiceAreaSearchForm(data)
        if service_area_search_form.is_valid():
            if service_area_search_form.is_null() is False:
                if service_area_search_form.fuzzy_search() is False:
                    query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
            else:
                query_set = ServiceArea.objects.filter(Q(is_active = True))

        else:
            query_set = ServiceArea.objects.filter(Q(is_active = True))
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'modify_form': service_area_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_delete(request, template_name='my.html', next='/', service_area_page='1',):
    """
    服务区域删除视图
    """
    page_title = u'删除服务区域'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'删除':
            service_area_delete_form = ServiceAreaDeleteForm(post_data)
            if service_area_delete_form.is_valid():
                service_area_delete_form.service_area_delete()
            else:
                pass
            data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                    'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                    }        
            service_area_search_form = ServiceAreaSearchForm(data)
            if service_area_search_form.is_valid():
                if service_area_search_form.is_null() is False:
                    if service_area_search_form.fuzzy_search() is False:
                        query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                               Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                    else:
                        service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                               Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    query_set = ServiceArea.objects.filter(Q(is_active = True))
            else:
                raise Http404('search form error!')
        else:
            service_area_delete_form = ServiceAreaDeleteForm()
            if submit_value == u'查询':
                service_area_search_form = ServiceAreaSearchForm(post_data)
                if service_area_search_form.is_valid():
                    service_area_search_form.save_to_session(request)
                    if service_area_search_form.is_null() is False:
                        if service_area_search_form.fuzzy_search() is False:
                            query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                                   Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                        else:
                            service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
                    else:
                        query_set = ServiceArea.objects.filter(Q(is_active = True))

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'delete_form': service_area_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_delete_form = ServiceAreaDeleteForm()
        data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                }        
        service_area_search_form = ServiceAreaSearchForm(data)
        if service_area_search_form.is_valid():
            if service_area_search_form.is_null() is False:
                if service_area_search_form.fuzzy_search() is False:
                    query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
            else:
                query_set = ServiceArea.objects.filter(Q(is_active = True))

        else:
            query_set = ServiceArea.objects.filter(Q(is_active = True))
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'delete_form': service_area_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

    
@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_list(request, template_name='my.html', next='/', service_area_page='1',):
    """
    服务区域查询视图
    """
    page_title = u'查询服务区域'

    if request.method == 'POST':
        post_data = request.POST.copy()
        service_area_search_form = ServiceAreaSearchForm(post_data)
        if service_area_search_form.is_valid():
            service_area_search_form.save_to_session(request)
            if service_area_search_form.is_null() is False:
                if service_area_search_form.fuzzy_search() is False:
                    query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                else:
                    service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
            else:
                query_set = ServiceArea.objects.filter(Q(is_active = True))

        else:
            query_set = None
        if query_set is not None:
            results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        data = {'service_area_name':request.session.get(gl.session_service_area_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_is_fuzzy, False),
                }        
#       print data['is_fuzzy']

        service_area_search_form = ServiceAreaSearchForm(data)
        if service_area_search_form.is_valid():
            if service_area_search_form.is_null() is False:
                if service_area_search_form.fuzzy_search() is False:
                    query_set = ServiceArea.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=service_area_search_form.cleaned_data['service_area_name']))
                else:
#                    print '********'
                    service_area_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = ServiceArea.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=service_area_search_form.cleaned_data['service_area_name']))
            else:
                query_set = ServiceArea.objects.filter(Q(is_active = True))

        else:
            query_set = ServiceArea.objects.filter(Q(is_active = True))
        results_page = pagination_results(service_area_page, query_set, settings.SERVICE_AREA_PER_PAGE)
        return render_to_response(template_name,
                                  {'search_form': service_area_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))



@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_department_add(request, template_name='my.html', next='/', service_area_department_page='1', service_area_index='1',):
    """
    服务区域单位部门添加视图，带添加预览功能！
    """
    page_title = u'关联单位部门'
    user = get_user(request)

    try:
        service_area = ServiceArea.objects.get(is_active=True, pk=int(service_area_index))
    except:
        raise Http404('search form error!')

    department_query_set = Department.objects.filter(is_active=True)
    query_set_choices = department_query_set.exclude(department_to_service_area__service_area__pk=service_area.pk,
                                                     department_to_service_area__is_active=True)
    choices = ()
    for query in query_set_choices:
#        print str(query.pk), query.name
        choices += (str(query.pk), query.name),

    
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加关联':
            service_area_department_add_form = ServiceAreaDepartmentAddForm(post_data)
            service_area_department_add_form.fields['service_area_department_name'].choices = choices
            if service_area_department_add_form.is_valid():
                service_area_department_add_form.service_area_department_add(service_area)
                query_set_choices = department_query_set.exclude(department_to_service_area__service_area__pk=service_area.pk,
                                                     department_to_service_area__is_active=True)
                choices = ()
                for query in query_set_choices:
#                    print str(query.pk), query.name
                    choices += (str(query.pk), query.name),
                service_area_department_add_form.fields['service_area_department_name'].choices = choices
            else:
                pass
                                   
            data = {'service_area_department_name':request.session.get(gl.session_service_area_department_name, u''),
                    'is_fuzzy':request.session.get(gl.session_service_area_department_is_fuzzy, False),
                    }

            service_area_department_search_form = ServiceAreaDepartmentSearchForm(data)
            if service_area_department_search_form.is_valid():
                query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                             department_to_service_area__is_active=True)
                if service_area_department_search_form.is_null() is False:
                    if service_area_department_search_form.fuzzy_search() is False:
                        query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                    else:
                        service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
                else:
                    query_set = query_set_temp
            else:
                raise Http404('search form error!')
        else:
            service_area_department_add_form = ServiceAreaDepartmentAddForm()
            service_area_department_add_form.fields['service_area_department_name'].choices = choices
            if submit_value == u'查询':
                service_area_department_search_form = ServiceAreaDepartmentSearchForm(post_data)
                if service_area_department_search_form.is_valid():
                    service_area_department_search_form.save_to_session(request)
                    query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                                 department_to_service_area__is_active=True)
                    if service_area_department_search_form.is_null() is False:
                        if service_area_department_search_form.fuzzy_search() is False:
                            query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                        else:
                            service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
                    else:
                        query_set = query_set_temp

                else:
#                    query_set = Service_Area_Department.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(service_area_department_page, query_set, settings.SERVICE_AREA_DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_department_search_form,
                                   'add_form': service_area_department_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'service_area_index':service_area_index,
                                   'service_area_name':service_area.name,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_department_add_form = ServiceAreaDepartmentAddForm()
        service_area_department_add_form.fields['service_area_department_name'].choices = choices
        data = {'service_area_department_name':request.session.get(gl.session_service_area_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_department_is_fuzzy, False),
                }
        service_area_department_search_form = ServiceAreaDepartmentSearchForm(data)
        if service_area_department_search_form.is_valid():
            query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                         department_to_service_area__is_active=True)
            if service_area_department_search_form.is_null() is False:
                if service_area_department_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                else:
                    service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
            else:
                query_set = query_set_temp

        else:
            query_set = None

        if query_set is not None:
            results_page = pagination_results(service_area_department_page, query_set, settings.SERVICE_AREA_DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_department_search_form,
                                   'add_form': service_area_department_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'service_area_index':service_area_index,
                                   'service_area_name':service_area.name,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_department_delete(request, template_name='my.html', next='/', service_area_department_page='1', service_area_index='1',):
    """
    服务区域单位部门删除视图，带添加预览功能！
    """
    page_title = u'关联单位部门'

    try:
        service_area = ServiceArea.objects.get(is_active=True, pk=int(service_area_index))
    except:
        raise Http404('search form error!')

    department_query_set = Department.objects.filter(is_active=True)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'删除关联':
            service_area_department_delete_form = ServiceAreaDepartmentDeleteForm(post_data)
            if service_area_department_delete_form.is_valid():
                service_area_department_delete_form.service_area_department_delete(service_area)
            else:
                pass
                                   
            data = {'service_area_department_name':request.session.get(gl.session_service_area_department_name, u''),
                    'is_fuzzy':request.session.get(gl.session_service_area_department_is_fuzzy, False),
                    }

            service_area_department_search_form = ServiceAreaDepartmentSearchForm(data)
            if service_area_department_search_form.is_valid():
                query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                             department_to_service_area__is_active=True)
                if service_area_department_search_form.is_null() is False:
                    if service_area_department_search_form.fuzzy_search() is False:
                        query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                    else:
                        service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
                else:
                    query_set = query_set_temp
            else:
                raise Http404('search form error!')
        else:
            service_area_department_delete_form = ServiceAreaDepartmentDeleteForm()
            if submit_value == u'查询':
                service_area_department_search_form = ServiceAreaDepartmentSearchForm(post_data)
                if service_area_department_search_form.is_valid():
                    service_area_department_search_form.save_to_session(request)
                    query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                                 department_to_service_area__is_active=True)
                    if service_area_department_search_form.is_null() is False:
                        if service_area_department_search_form.fuzzy_search() is False:
                            query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                        else:
                            service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
                    else:
                        query_set = query_set_temp

                else:
#                    query_set = Service_Area_Department.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(service_area_department_page, query_set, settings.SERVICE_AREA_DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_department_search_form,
                                   'delete_form': service_area_department_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'service_area_index':service_area_index,
                                   'service_area_name':service_area.name,
                                   },
                                  context_instance=RequestContext(request))
    else:
        service_area_department_delete_form = ServiceAreaDepartmentDeleteForm()
        data = {'service_area_department_name':request.session.get(gl.session_service_area_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_department_is_fuzzy, False),
                }
        service_area_department_search_form = ServiceAreaDepartmentSearchForm(data)
        if service_area_department_search_form.is_valid():
            query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                         department_to_service_area__is_active=True)
            if service_area_department_search_form.is_null() is False:
                if service_area_department_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                else:
                    service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
            else:
                query_set = query_set_temp

        else:
            query_set = None

        if query_set is not None:
            results_page = pagination_results(service_area_department_page, query_set, settings.SERVICE_AREA_DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_department_search_form,
                                   'delete_form': service_area_department_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'service_area_index':service_area_index,
                                   'service_area_name':service_area.name,
                                   },
                                  context_instance=RequestContext(request))
    
@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_department_list(request, template_name='my.html', next='/', service_area_department_page='1', service_area_index='1',):
    """
    服务区域单位部门列表视图，带添加预览功能！
    """
    page_title = u'显示关联单位部门列表'

    try:
        service_area = ServiceArea.objects.get(is_active=True, pk=int(service_area_index))
    except:
        raise Http404('search form error!')

    department_query_set = Department.objects.filter(is_active=True)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        service_area_department_search_form = ServiceAreaDepartmentSearchForm(post_data)
        if service_area_department_search_form.is_valid():
            service_area_department_search_form.save_to_session(request)
            query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                         department_to_service_area__is_active=True)
            if service_area_department_search_form.is_null() is False:
                if service_area_department_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                else:
                    service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
            else:
                query_set = query_set_temp
                
        else:
#                    query_set = Service_Area_Department.objects.filter(Q(is_active = True))
            query_set = None
        if query_set is not None:
            results_page = pagination_results(service_area_department_page, query_set, settings.SERVICE_AREA_DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_department_search_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'service_area_index':service_area_index,
                                   'service_area_name':service_area.name,
                                   },
                                  context_instance=RequestContext(request))
    else:
        data = {'service_area_department_name':request.session.get(gl.session_service_area_department_name, u''),
                'is_fuzzy':request.session.get(gl.session_service_area_department_is_fuzzy, False),
                }
        service_area_department_search_form = ServiceAreaDepartmentSearchForm(data)
        if service_area_department_search_form.is_valid():
            query_set_temp = department_query_set.filter(department_to_service_area__service_area__pk=service_area.pk,
                                                         department_to_service_area__is_active=True)
            if service_area_department_search_form.is_null() is False:
                if service_area_department_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=service_area_department_search_form.cleaned_data['service_area_department_name'])
                else:
                    service_area_department_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=service_area_department_search_form.cleaned_data['service_area_department_name'])
            else:
                query_set = query_set_temp

        else:
            query_set = None

        if query_set is not None:
            results_page = pagination_results(service_area_department_page, query_set, settings.SERVICE_AREA_DEPARTMENT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': service_area_department_search_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'service_area_index':service_area_index,
                                   'service_area_name':service_area.name,
                                   },
                                  context_instance=RequestContext(request))

@cache_page(60 * 15)
def service_area_name_ajax(request, template_name='my.html', next='/'):
    if request.is_ajax():
        result = []
        if request.method == 'GET':
#            print '******************8'
            query_set = ServiceArea.objects.filter(is_active=True)
            result = [ x.name for x in query_set]
#            print result
        else:
            pass
        json = simplejson.dumps(result)
#        print json
        return HttpResponse(json, mimetype='application/json')
    else:
        raise Http404('Invalid Request!')
 
