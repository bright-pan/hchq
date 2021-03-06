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
from django.contrib.auth.models import *
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from account.forms import *
from untils.my_paginator import pagination_results
from untils import gl, download
from hchq import settings
from report.user_report import user_report

from check_project.models import CheckProject
from check_object.models import CheckObject
from check_result.models import CheckResult

# Create your views here.
import pygal
from pygal.style import LightGreenStyle
import datetime

class MyConfig(pygal.Config):
    width=1024
    height=768
    x_label_rotation=90
    human_readable = True
    truncate_label=100
    margin = 60
    legend_box_size=18
    style=LightGreenStyle

def get_service_area_statistics():
    service_area_statistics = cache.get('service_area_statistics')
    if service_area_statistics is None:
        service_area_statistics = {}
        check_project = CheckProject.objects.get(is_setup=True)
        check_project_endtime = datetime.datetime(check_project.end_time.year,
                                                  check_project.end_time.month,
                                                  check_project.end_time.day,
                                                  23, 59, 59)
        qs_check_object = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                   updated_at__lt=check_project_endtime)
        qs_check_result = CheckResult.objects.filter(check_project=check_project, is_latest=True)
        qs_service_area = ServiceArea.objects.filter(is_active=True).order_by('id')

        service_area_statistics["qs_check_object"] = qs_check_object.count()
        service_area_statistics["qs_check_result"] = qs_check_result.count()
        service_area_statistics['check_project_name'] = check_project.name
        service_area_name_list = []
        check_object_count_list = []
        check_count_list = []
        pregnant_count_list = []
        special_count_list = []
        for service_area_object in qs_service_area:
            service_area_name_list.append(service_area_object.name)
            check_object_count = qs_check_object.filter(service_area_department__service_area=service_area_object).count()
            check_object_count_list.append(check_object_count)
            check_result = qs_check_result.filter(check_object__service_area_department__service_area=service_area_object)
            check_count = check_result.count()
            check_count_list.append(check_count)
            pregnant_count = check_result.filter(result__startswith='pregnant').count()
            pregnant_count_list.append(pregnant_count)
            special_count = check_result.filter(result__contains='special').count()
            special_count_list.append(special_count)
        service_area_statistics["service_area_name"] = service_area_name_list
        service_area_statistics["check_object_count"] = check_object_count_list
        service_area_statistics["check_count"] = check_count_list
        service_area_statistics["pregnant_count"] = pregnant_count_list
        service_area_statistics["special_count"] = special_count_list
        cache.set('service_area_statistics', service_area_statistics, 2*60*60)
    return service_area_statistics

@cache_page(60*60)
def get_bar_chart(request, template_name = 'account/login.html', next='/'):
    service_area_statistics = get_service_area_statistics()
    my_config = MyConfig()
    bar_chart = pygal.Bar(my_config)
    bar_chart.title = u'%s-各服务区域统计' % service_area_statistics.get('check_project_name',u'无检查项目')
    bar_chart.x_labels = service_area_statistics["service_area_name"]
    bar_chart.add(u"总人数", service_area_statistics["check_object_count"])
    bar_chart.add(u'已检人数', service_area_statistics["check_count"])
    return HttpResponse(bar_chart.render(), content_type='image/svg+xml')

@cache_page(60*60)
def get_pie_chart(request, template_name = 'account/login.html', next='/'):
    service_area_statistics = get_service_area_statistics()
    my_config = MyConfig()
    pie_chart = pygal.Pie(my_config)
    pie_chart.title = u'%s-总完成度' % service_area_statistics.get('check_project_name',u'无检查项目')
    pie_chart.add(u'已检对象', service_area_statistics.get('qs_check_result',0)*1.0/service_area_statistics.get('qs_check_object',1))
    pie_chart.add(u'未检对象', (service_area_statistics.get('qs_check_object',0) - service_area_statistics.get('qs_check_result',0))*1.0/service_area_statistics.get('qs_check_object',1))
    return HttpResponse(pie_chart.render(), content_type='image/svg+xml')

@cache_page(60*60)
def get_dot_chart(request, template_name = 'account/login.html', next='/'):
    service_area_statistics = get_service_area_statistics()
    my_config = MyConfig()
    dot_chart = pygal.Dot(my_config)
    dot_chart.title = u'%s-各类人数统计' % service_area_statistics.get('check_project_name',u'无检查项目')
    dot_chart.x_labels = service_area_statistics["service_area_name"]
    dot_chart.add(u"总人数", service_area_statistics["check_object_count"])
    dot_chart.add(u'已检人数', service_area_statistics["check_count"])
    dot_chart.add(u'有孕人数', service_area_statistics["pregnant_count"])
    dot_chart.add(u'特检人数', service_area_statistics["special_count"])
    return HttpResponse(dot_chart.render(), content_type='image/svg+xml')

def my_layout_test(request, template_name = 'my.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))


@csrf_protect
@never_cache
def login(request, template_name = 'account/login.html', next='/'):

    page_title = u'用户登入'
    login_form = None
    if request.method == 'POST':
        post_data = request.POST.copy()
        #print(request.META['HTTP_ORIGIN'] + next)
        login_form = LoginForm(post_data)
        if login_form.is_valid():
            from django.contrib.auth import login
            login(request, login_form.get_user())
            #return HttpResponseRedirect(request.META['HTTP_ORIGIN'] + next)
            return HttpResponseRedirect(next)
        else:
            pass
    else:
        login_form = LoginForm()

    return render_to_response(template_name, {'form': login_form, 'page_title': page_title}, context_instance=RequestContext(request))

def exit(request, template_name = 'my.html', next = '/'):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect(next)

@csrf_protect
@login_required

def person_password_modify(request, template_name = '', next = '/'):

    page_title = u'修改密码'
    user = get_user(request)
    post_data = None
    modify_password_form = None
    fault = False
    if request.method == 'POST':
        post_data = request.POST.copy()
        modify_password_form = ModifyPasswordForm(post_data)
        if modify_password_form.is_valid():
            if modify_password_form.password_save(user) is True:
                return HttpResponseRedirect(next)
            else:
                fault = True
                pass
        else:
            pass
    else:
        modify_password_form = ModifyPasswordForm()

    return render_to_response(template_name,
                              {'form': modify_password_form,
                               'fault': fault,
                               'page_title': page_title},
                              context_instance=RequestContext(request))


@login_required
def person_management(request, template_name = 'my.html', next = '/'):

    page_title = u'个人信息'
    return render_to_response(template_name,
                              {'page_title': page_title},
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
def test_person_password_modify(request, template_name = 'my.html', next = '/'):

    page_title = u'密码修改'
    return render_to_response(template_name, {'page_title': page_title}, context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.role_management')
def role_add(request, template_name='my.html', next='/', role_page='1'):
    """
    角色添加视图，带添加预览功能！
    """
    page_title = u'添加角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'添加':
            role_add_form = RoleAddForm(post_data)
            if role_add_form.is_valid():
                role_add_form.role_add()
            else:
                pass
            data = {'role_name':request.session.get(gl.session_role_name, u''),
                    'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                    }
#            print data['role_name']
#            print data['is_fuzzy']
            role_search_form = RoleSearchForm(data)
            if role_search_form.is_valid():
                if role_search_form.is_null() is False:
                    if role_search_form.fuzzy_search() is False:
                        query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                    else:
                        role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
                else:
                    query_set = Group.objects.all()
            else:
                raise Http404('search form error!')
        else:
            role_add_form = RoleAddForm()
            if submit_value == u'查询':
                role_search_form = RoleSearchForm(post_data)
                if role_search_form.is_valid():
                    role_search_form.save_to_session(request)
                    if role_search_form.is_null() is False:
                        if role_search_form.fuzzy_search() is False:
                            query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                        else:
                            role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
                    else:
                        query_set = Group.objects.all()
                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'add_form': role_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        role_add_form = RoleAddForm()
        data = {'role_name':request.session.get(gl.session_role_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                }
        role_search_form = RoleSearchForm(data)
        if role_search_form.is_valid():
            if role_search_form.is_null() is False:
                if role_search_form.fuzzy_search() is False:
                    query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                else:
                    role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
            else:
                query_set = Group.objects.all()
        else:
            query_set = Group.objects.all()
        results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'add_form': role_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.role_management')
def role_delete(request, template_name='my.html', next='/', role_page='1',):
    """
    角色删除视图
    """
    page_title = u'删除角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'删除':
            role_delete_form = RoleDeleteForm(post_data)
            if role_delete_form.is_valid():
                role_delete_form.role_delete()
            else:
                pass
            data = {'role_name':request.session.get(gl.session_role_name, u''),
                    'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                    }
            role_search_form = RoleSearchForm(data)
            if role_search_form.is_valid():
                if role_search_form.is_null() is False:
                    if role_search_form.fuzzy_search() is False:
                        query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                    else:
                        role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
                else:
                    query_set = Group.objects.all()
            else:
                raise Http404('search form error!')
        else:
            role_delete_form = RoleDeleteForm()
            if submit_value == u'查询':
                role_search_form = RoleSearchForm(post_data)
                if role_search_form.is_valid():
                    role_search_form.save_to_session(request)
                    if role_search_form.is_null() is False:
                        if role_search_form.fuzzy_search() is False:
                            query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                        else:
                            role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
                    else:
                        query_set = Group.objects.all()

                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'delete_form': role_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        role_delete_form = RoleDeleteForm()
        data = {'role_name':request.session.get(gl.session_role_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                }
        role_search_form = RoleSearchForm(data)
        if role_search_form.is_valid():
            if role_search_form.is_null() is False:
                if role_search_form.fuzzy_search() is False:
                    query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                else:
                    role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
            else:
                query_set = Group.objects.all()

        else:
            query_set = Group.objects.all()
        results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'delete_form': role_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


@csrf_protect
@login_required
@permission_required('department.role_management')
def role_modify(request, template_name='my.html', next='/', role_page='1',):
    """
    角色修改视图
    """
    page_title = u'修改角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'修改':
            role_modify_form = RoleModifyForm(post_data)
            if role_modify_form.is_valid():
                role_modify_form.role_modify()
            else:
                pass
            data = {'role_name':request.session.get(gl.session_role_name, u''),
                    'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                    }
            role_search_form = RoleSearchForm(data)
            if role_search_form.is_valid():
                if role_search_form.is_null() is False:
                    if role_search_form.fuzzy_search() is False:
                        query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                    else:
                        role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
                else:
                    query_set = Group.objects.all()

            else:
                raise Http404('search form error!')
        else:
            role_modify_form = RoleModifyForm()
            if submit_value == u'查询':
                role_search_form = RoleSearchForm(post_data)
                if role_search_form.is_valid():
                    role_search_form.save_to_session(request)
                    if role_search_form.is_null() is False:
                        if role_search_form.fuzzy_search() is False:
                            query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                        else:
                            role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
                    else:
                        query_set = Group.objects.all()
                else:
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'modify_form': role_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        role_modify_form = RoleModifyForm()
        data = {'role_name':request.session.get(gl.session_role_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                }
        role_search_form = RoleSearchForm(data)
        if role_search_form.is_valid():
            if role_search_form.is_null() is False:
                if role_search_form.fuzzy_search() is False:
                    query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                else:
                    role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
            else:
                query_set = Group.objects.all()

        else:
            query_set = Group.objects.all()
        results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)

        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'modify_form': role_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


@csrf_protect
@login_required
@permission_required('department.role_management')
def role_list(request, template_name='my.html', next='/', role_page='1',):
    """
    角色查询视图
    """
    page_title = u'查询角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        role_search_form = RoleSearchForm(post_data)
        if role_search_form.is_valid():
            role_search_form.save_to_session(request)
            if role_search_form.is_null() is False:
                if role_search_form.fuzzy_search() is False:
                    query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                else:
                    role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
            else:
                query_set = Group.objects.all()

        else:
            query_set = None
        if query_set is not None:
            results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        data = {'role_name':request.session.get(gl.session_role_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_is_fuzzy, False),
                }
        role_search_form = RoleSearchForm(data)
        if role_search_form.is_valid():
            if role_search_form.is_null() is False:
                if role_search_form.fuzzy_search() is False:
                    query_set = Group.objects.filter(name__startswith=role_search_form.cleaned_data['role_name'])
                else:
                    role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Group.objects.filter(name__icontains=role_search_form.cleaned_data['role_name'])
            else:
                query_set = Group.objects.all()
        else:
            query_set = Group.objects.all()

        results_page = pagination_results(role_page, query_set, settings.ROLE_PER_PAGE)
        return render_to_response(template_name,
                                  {'search_form': role_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))



@csrf_protect
@login_required
@permission_required('department.role_management')
def role_permission_add(request, template_name='my.html', next='/', role_permission_page='1', role_index='1',):
    """
    角色权限添加视图，带添加预览功能！
    """
    page_title = u'关联权限'
    user = get_user(request)

    try:
        role = Group.objects.get(pk=int(role_index))
    except:
        raise Http404('search form error!')

    permission_query_set = Permission.objects.all()
    query_set_choices = permission_query_set.exclude(group__pk=role.pk)
    choices = ()
    for query in query_set_choices:
#        print str(query.pk), query.name
        choices += (str(query.pk), query.name),


    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'添加关联':
            role_permission_add_form = RolePermissionAddForm(post_data)
            role_permission_add_form.fields['role_permission_name'].choices = choices
            if role_permission_add_form.is_valid():
                role_permission_add_form.role_permission_add(role)
                query_set_choices = permission_query_set.exclude(group__pk=role.pk)
                choices = ()
                for query in query_set_choices:
#                    print str(query.pk), query.name
                    choices += (str(query.pk), query.name),
                role_permission_add_form.fields['role_permission_name'].choices = choices
            else:
                pass

            data = {'role_permission_name':request.session.get(gl.session_role_permission_name, u''),
                    'is_fuzzy':request.session.get(gl.session_role_permission_is_fuzzy, False),
                    }

            role_permission_search_form = RolePermissionSearchForm(data)
            if role_permission_search_form.is_valid():
                query_set_temp = permission_query_set.filter(group__pk=role.pk)
                if role_permission_search_form.is_null() is False:
                    if role_permission_search_form.fuzzy_search() is False:
                        query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                    else:
                        role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
                else:
                    query_set = query_set_temp
            else:
                raise Http404('search form error!')
        else:
            role_permission_add_form = RolePermissionAddForm()
            role_permission_add_form.fields['role_permission_name'].choices = choices
            if submit_value == u'查询':
                role_permission_search_form = RolePermissionSearchForm(post_data)
                if role_permission_search_form.is_valid():
                    role_permission_search_form.save_to_session(request)
                    query_set_temp = permission_query_set.filter(group__pk=role.pk)

                    if role_permission_search_form.is_null() is False:
                        if role_permission_search_form.fuzzy_search() is False:
                            query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                        else:
                            role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
                    else:
                        query_set = query_set_temp

                else:
#                    query_set = role_permission.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(role_permission_page, query_set, settings.ROLE_PERMISSION_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_permission_search_form,
                                   'add_form': role_permission_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'role_index':role_index,
                                   'role_name':role.name,
                                   },
                                  context_instance=RequestContext(request))
    else:
        role_permission_add_form = RolePermissionAddForm()
        role_permission_add_form.fields['role_permission_name'].choices = choices
        data = {'role_permission_name':request.session.get(gl.session_role_permission_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_permission_is_fuzzy, False),
                }
        role_permission_search_form = RolePermissionSearchForm(data)
        if role_permission_search_form.is_valid():
            query_set_temp = permission_query_set.filter(group__pk=role.pk)

            if role_permission_search_form.is_null() is False:
                if role_permission_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                else:
                    role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
            else:
                query_set = query_set_temp

        else:
            query_set = None

        if query_set is not None:
            results_page = pagination_results(role_permission_page, query_set, settings.ROLE_PERMISSION_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_permission_search_form,
                                   'add_form': role_permission_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'role_index':role_index,
                                   'role_name':role.name,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.role_management')
def role_permission_delete(request, template_name='my.html', next='/', role_permission_page='1', role_index='1',):
    """
    角色权限删除视图，带添加预览功能！
    """
    page_title = u'关联权限'

    try:
        role = Group.objects.get(pk=int(role_index))
    except:
        raise Http404('search form error!')

    permission_query_set = Permission.objects.all()

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'删除关联':
            role_permission_delete_form = RolePermissionDeleteForm(post_data)
            if role_permission_delete_form.is_valid():
                role_permission_delete_form.role_permission_delete(role)
            else:
                pass

            data = {'role_permission_name':request.session.get(gl.session_role_permission_name, u''),
                    'is_fuzzy':request.session.get(gl.session_role_permission_is_fuzzy, False),
                    }

            role_permission_search_form = RolePermissionSearchForm(data)
            if role_permission_search_form.is_valid():
                query_set_temp = permission_query_set.filter(group__pk=role.pk)

                if role_permission_search_form.is_null() is False:
                    if role_permission_search_form.fuzzy_search() is False:
                        query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                    else:
                        role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                        query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
                else:
                    query_set = query_set_temp
            else:
                raise Http404('search form error!')
        else:
            role_permission_delete_form = RolePermissionDeleteForm()
            if submit_value == u'查询':
                role_permission_search_form = RolePermissionSearchForm(post_data)
                if role_permission_search_form.is_valid():
                    role_permission_search_form.save_to_session(request)
                    query_set_temp = permission_query_set.filter(group__pk=role.pk)

                    if role_permission_search_form.is_null() is False:
                        if role_permission_search_form.fuzzy_search() is False:
                            query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                        else:
                            role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                            query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
                    else:
                        query_set = query_set_temp

                else:
#                    query_set = role_permission.objects.filter(Q(is_active = True))
                    query_set = None
            else:
                raise Http404('search form error!')
        if query_set is not None:
            results_page = pagination_results(role_permission_page, query_set, settings.ROLE_PERMISSION_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_permission_search_form,
                                   'delete_form': role_permission_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'role_index':role_index,
                                   'role_name':role.name,
                                   },
                                  context_instance=RequestContext(request))
    else:
        role_permission_delete_form = RolePermissionDeleteForm()
        data = {'role_permission_name':request.session.get(gl.session_role_permission_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_permission_is_fuzzy, False),
                }
        role_permission_search_form = RolePermissionSearchForm(data)
        if role_permission_search_form.is_valid():
            query_set_temp = permission_query_set.filter(group__pk=role.pk)

            if role_permission_search_form.is_null() is False:
                if role_permission_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                else:
                    role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
            else:
                query_set = query_set_temp

        else:
            query_set = None

        if query_set is not None:
            results_page = pagination_results(role_permission_page, query_set, settings.ROLE_PERMISSION_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_permission_search_form,
                                   'delete_form': role_permission_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'role_index':role_index,
                                   'role_name':role.name,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.role_management')
def role_permission_list(request, template_name='my.html', next='/', role_permission_page='1', role_index='1',):
    """
    角色权限列表视图，带添加预览功能！
    """
    page_title = u'显示关联权限列表'

    try:
        role = Group.objects.get(pk=int(role_index))
    except:
        raise Http404('search form error!')

    permission_query_set = Permission.objects.all()

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        role_permission_search_form = RolePermissionSearchForm(post_data)
        if role_permission_search_form.is_valid():
            role_permission_search_form.save_to_session(request)
            query_set_temp = permission_query_set.filter(group__pk=role.pk)

            if role_permission_search_form.is_null() is False:
                if role_permission_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                else:
                    role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
            else:
                query_set = query_set_temp

        else:
#                    query_set = role_permission.objects.filter(Q(is_active = True))
            query_set = None
        if query_set is not None:
            results_page = pagination_results(role_permission_page, query_set, settings.ROLE_PERMISSION_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_permission_search_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'role_index':role_index,
                                   'role_name':role.name,
                                   },
                                  context_instance=RequestContext(request))
    else:
        data = {'role_permission_name':request.session.get(gl.session_role_permission_name, u''),
                'is_fuzzy':request.session.get(gl.session_role_permission_is_fuzzy, False),
                }
        role_permission_search_form = RolePermissionSearchForm(data)
        if role_permission_search_form.is_valid():
            query_set_temp = permission_query_set.filter(group__pk=role.pk)

            if role_permission_search_form.is_null() is False:
                if role_permission_search_form.fuzzy_search() is False:
                    query_set = query_set_temp.filter(name__startswith=role_permission_search_form.cleaned_data['role_permission_name'])
                else:
                    role_permission_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = query_set_temp.filter(name__icontains=role_permission_search_form.cleaned_data['role_permission_name'])
            else:
                query_set = query_set_temp

        else:
            query_set = None

        if query_set is not None:
            results_page = pagination_results(role_permission_page, query_set, settings.ROLE_PERMISSION_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': role_permission_search_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   'role_index':role_index,
                                   'role_name':role.name,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.account_add')
def account_add(request, template_name='my.html', next='/', account_page='1'):
    """
    系统用户添加视图，带添加预览功能！
    """
    page_title = u'添加系统用户'
    user = get_user(request)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'添加':
            account_add_form = AccountAddForm(post_data)
            if account_add_form.is_valid():
                account_profile = account_add_form.add()
                if account_profile is not None:
                    return HttpResponseRedirect('account/show/%s' % account_profile.id)
                else:
                    raise Http404('Invalid Request!')
            else:
                account_add_form.init_permission(user)
                return render_to_response(template_name,
                                          {'add_form': account_add_form,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))


        else:
            raise Http404('Invalid Request!')
    else:
        account_add_form = AccountAddForm()
        account_add_form.init_permission(user)
        return render_to_response(template_name,
                                  {'add_form': account_add_form,
                                  'page_title': page_title,
                                  },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
#@permission_required('department.account_list')
#@permission_required('department.account_modify')
#@permission_required('department.account_delete')
@user_passes_test(lambda u: (u.has_perm('department.account_list') or u.has_perm('department.account_modify') or u.has_perm('department.account_delete') or u.has_perm('department.account_add')))
def account_show(request, template_name='', next='', account_index='1'):
    """
    系统用户详细信息显示。
    """
    page_title=u'系统用户详情'
    success = False
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'密码重置':
            try:
                account_id = int(account_index)
            except ValueError:
                raise Http404('Invalid Request!')
            try:
                result = UserProfile.objects.get(pk=account_id, user__is_active=True, user__is_superuser=False, user__is_staff=False)
            except ObjectDoesNotExist:
                raise Http404('Invalid Request!')
            if request.user.has_perm('department.account_modify'):
                result.user.set_password(settings.ACCOUNT_DEFAULT_PASSWORD)
                result.user.save()
                success = True
            else:
                success = False
        else:
            raise Http404('Invalid Request!')

    else:
        try:
            account_id = int(account_index)
        except ValueError:
            raise Http404('Invalid Request!')
        try:
            result = UserProfile.objects.get(pk=account_id, user__is_active=True, user__is_superuser=False, user__is_staff=False)
        except ObjectDoesNotExist:
            raise Http404('Invalid Request!')

    return render_to_response(template_name,
                              {'result': result,
                               'success': success,
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.account_modify')
def account_modify(request, template_name='my.html', next_template_name='my.html', account_page='1',):
    """
    系统用户修改视图
    """
    page_title = u'编辑系统用户'
    user = get_user(request)
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'编辑':
            account_modify_form = AccountModifyForm(post_data)
            if account_modify_form.is_valid():
                account_modify_object = account_modify_form.object()
#                print account_modify_object
                account_detail_modify_form = AccountDetailModifyForm()
                account_detail_modify_form.set_value(account_modify_object, user)
                page_title = u'修改系统用户'
                return render_to_response(next_template_name,
                                          {'detail_modify_form': account_detail_modify_form,
                                           'account_name': account_modify_object.username,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
            else:
                pass
            account_search_form = AccountSearchForm(AccountSearchForm().data_from_session(request))
            account_search_form.init_from_session(request)
            if account_search_form.is_valid():
                query_set = account_search_form.search(request)
                results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
            else:
                results_page = None
        else:
            if submit_value == u'查询':
                account_search_form = AccountSearchForm(post_data)
                account_modify_form = AccountModifyForm()
                if account_search_form.is_valid():
                    account_search_form.data_to_session(request)
                    account_search_form.init_from_session(request)
                    query_set = account_search_form.search(request)
                    results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
                else:
                    results_page = None
            else:
                if submit_value == u'导出用户报表':
                    account_search_form = AccountSearchForm(post_data)
                    if account_search_form.is_valid():
                        account_search_form.data_to_session(request)
                        account_search_form.init_from_session(request)
                        query_set = account_search_form.search(request)
                        return download.down_zipfile(request, user_report(query_set, request))
                    else:
                        results_page = None
                        return render_to_response(template_name,
                                                  {'search_form': account_search_form,
                                                   'page_title': page_title,
                                                   'results_page': results_page,
                                                   },
                                                  context_instance=RequestContext(request))

                else:
                    raise Http404('Invalid Request!')
        return render_to_response(template_name,
                                  {'search_form': account_search_form,
                                   'modify_form': account_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        account_modify_form = AccountModifyForm()
        account_search_form = AccountSearchForm(AccountSearchForm().data_from_session(request))
        account_search_form.init_from_session(request)
        if account_search_form.is_valid():
            query_set = account_search_form.search(request)
            results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': account_search_form,
                                   'modify_form': account_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.account_modify')
def account_detail_modify(request, template_name='my.html', next='/', account_page='1',):
    """
    系统用户修改视图
    """

    page_title = u'编辑系统用户'
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'修改':
            account_detail_modify_form = AccountDetailModifyForm(post_data)
            if account_detail_modify_form.is_valid():
                account_profile = account_detail_modify_form.detail_modify()
                if account_profile is not None:
                    return HttpResponseRedirect('account/show/%s' % account_profile.id)
                else:
                    raise Http404('Invalid Request!')
            else:
                account_id = int(account_detail_modify_form.data.get('id'))
                account_object = User.objects.get(pk=account_id)
                return render_to_response(template_name,
                                          {'detail_modify_form': account_detail_modify_form,
                                           'account_name': account_object.username,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))

        else:
            raise Http404('Invalid Request!')
    else:
        raise Http404('Invalid Request!')

@csrf_protect
@login_required
@permission_required('department.account_delete')
def account_delete(request, template_name='my.html', next='/', account_page='1',):
    """
    系统用户删除视图
    """
    page_title = u'删除系统用户'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'删除':
            account_delete_form = AccountDeleteForm(post_data)
            if account_delete_form.is_valid():
                account_delete_form.delete()
            else:
                pass
            account_search_form = AccountSearchForm(AccountSearchForm().data_from_session(request))
            account_search_form.init_from_session(request)
            if account_search_form.is_valid():
                query_set = account_search_form.search(request)
                results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
            else:
                results_page = None
        else:
            if submit_value == u'查询':
                account_search_form = AccountSearchForm(post_data)
                account_delete_form = AccountDeleteForm()
                if account_search_form.is_valid():
                    account_search_form.data_to_session(request)
                    account_search_form.init_from_session(request)
                    query_set = account_search_form.search(request)
                    results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
                else:
                    results_page = None
            else:
                if submit_value == u'导出用户报表':
                    account_search_form = AccountSearchForm(post_data)
                    if account_search_form.is_valid():
                        account_search_form.data_to_session(request)
                        account_search_form.init_from_session(request)
                        query_set = account_search_form.search(request)
                        return download.down_zipfile(request, user_report(query_set, request))
                    else:
                        results_page = None
                        return render_to_response(template_name,
                                                  {'search_form': account_search_form,
                                                   'page_title': page_title,
                                                   'results_page': results_page,
                                                   },
                                                  context_instance=RequestContext(request))

                else:
                    raise Http404('Invalid Request!')
        return render_to_response(template_name,
                                  {'search_form': account_search_form,
                                   'delete_form': account_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        account_delete_form = AccountDeleteForm()
        account_search_form = AccountSearchForm(AccountSearchForm().data_from_session(request))
        account_search_form.init_from_session(request)
        if account_search_form.is_valid():
            query_set = account_search_form.search(request)
            results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': account_search_form,
                                   'delete_form': account_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


@csrf_protect
@login_required
@permission_required('department.account_list')
def account_list(request, template_name='my.html', next='/', account_page='1',):
    """
    系统用户查询视图
    """
    page_title = u'查询系统用户'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', u'')
        if submit_value == u'查询':
            account_search_form = AccountSearchForm(post_data)
            if account_search_form.is_valid():
                account_search_form.data_to_session(request)
                account_search_form.init_from_session(request)
                query_set = account_search_form.search(request)
                results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
            else:
                results_page = None
            return render_to_response(template_name,
                                      {'search_form': account_search_form,
                                       'page_title': page_title,
                                       'results_page': results_page,
                                       },
                                      context_instance=RequestContext(request))
        else:
            if submit_value == u'导出用户报表':
                account_search_form = AccountSearchForm(post_data)
                if account_search_form.is_valid():
                    account_search_form.data_to_session(request)
                    account_search_form.init_from_session(request)
                    query_set = account_search_form.search(request)
                    return download.down_zipfile(request, user_report(query_set, request))
                else:
                    results_page = None
                    return render_to_response(template_name,
                                              {'search_form': account_search_form,
                                               'page_title': page_title,
                                               'results_page': results_page,
                                               },
                                              context_instance=RequestContext(request))

            else:
                raise Http404('Invalid Request!')
    else:
        account_search_form = AccountSearchForm(AccountSearchForm().data_from_session(request))
        account_search_form.init_from_session(request)
        if account_search_form.is_valid():
            query_set = account_search_form.search(request)
            results_page = pagination_results(account_page, query_set, settings.ACCOUNT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': account_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))

@cache_page(60 * 15)
def role_name_ajax(request, template_name='my.html', next='/'):

    if request.is_ajax():
        result = []
        if request.method == 'GET':
            query_set = Group.objects.all()
            result = [ x.name for x in query_set]
#            print result
        else:
            pass
        json = simplejson.dumps(result)
#        print json
        return HttpResponse(json, mimetype='application/json')
    else:

        raise Http404('Invalid Request!')
