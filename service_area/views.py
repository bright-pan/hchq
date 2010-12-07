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

from hchq.service_area.forms import ServiceAreaAddForm, ServiceAreaModifyForm, ServiceAreaDeleteForm, ServiceAreaSearchForm
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

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加':
            service_area_add_form = ServiceAreaAddForm(post_data)
            if service_area_add_form.is_valid():
                service_area_add_form.service_area_add(user)
            else:
                pass
            data = {'service_area_name':request.session.get('service_area_name', u''),
                    'is_fuzzy':request.session.get('is_fuzzy', False),
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
        data = {'service_area_name':request.session.get('service_area_name', u''),
                'is_fuzzy':request.session.get('is_fuzzy', False),
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
def service_area_modify(request, template_name='my.html', next='/', service_area_page='1',):
    """
    服务区修改视图
    """
    page_title = u'添加服务区域'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'修改':
            service_area_modify_form = ServiceAreaModifyForm(post_data)
            if service_area_modify_form.is_valid():
                service_area_modify_form.service_area_modify()
            else:
                pass
            data = {'service_area_name':request.session.get('service_area_name', u''),
                    'is_fuzzy':request.session.get('is_fuzzy', False),
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
        data = {'service_area_name':request.session.get('service_area_name', u''),
                'is_fuzzy':request.session.get('is_fuzzy', False),
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
    服务区删除视图
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
            data = {'service_area_name':request.session.get('service_area_name', u''),
                    'is_fuzzy':request.session.get('is_fuzzy', False),
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
        data = {'service_area_name':request.session.get('service_area_name', u''),
                'is_fuzzy':request.session.get('is_fuzzy', False),
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
    服务区查询视图
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
        data = {'service_area_name':request.session.get('service_area_name', u''),
                'is_fuzzy':request.session.get('is_fuzzy', False),
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
