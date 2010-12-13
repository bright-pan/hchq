#coding=utf-8
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q
from hchq.account.forms import *
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings

# Create your views here.
def my_layout_test(request, template_name = 'my.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))

@csrf_protect
@never_cache
def login(request, template_name = 'account/login.html', next = '/'):

    page_title = u'用户登入'
    login_form = None
    if request.method == 'POST':
        post_data = request.POST.copy()
        login_form = LoginForm(post_data)
        if login_form.is_valid():
            from django.contrib.auth import login
            login(request, login_form.get_user())
            return HttpResponseRedirect(next)
        else:
            return render_to_response(template_name, {'form': login_form, 'page_title': page_title}, context_instance=RequestContext(request))
    else:
        login_form = LoginForm()
        return render_to_response(template_name, {'form': login_form, 'page_title': page_title}, context_instance=RequestContext(request))

def exit(request, template_name = 'my.html', next = '/'):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect(next)

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def person_password_modify(request, template_name = '', next = '/'):
    
    page_title = u'修改密码'
    user = get_user(request)
    post_data = None
    modify_password_form = None
    if request.method == 'POST':
        post_data = request.POST.copy()
        modify_password_form = ModifyPasswordForm(post_data)
        if modify_password_form.is_valid():
            modify_password_form.password_save(user)
            return HttpResponseRedirect(next)
        else:
            return render_to_response(template_name, {'form': modify_password_form, 'page_title': page_title}, context_instance=RequestContext(request))
    else:
        modify_password_form = ModifyPasswordForm()
        return render_to_response(template_name, {'form': modify_password_form, 'page_title': page_title}, context_instance=RequestContext(request))        


@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def person_management(request, template_name = 'my.html', next = '/'):
    
    page_title = u'个人信息'
    return render_to_response(template_name, {'page_title': page_title}, context_instance=RequestContext(request))    

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def test_person_password_modify(request, template_name = 'my.html', next = '/'):
    
    page_title = u'密码修改'
    return render_to_response(template_name, {'page_title': page_title}, context_instance=RequestContext(request))

@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def role_add(request, template_name='my.html', next='/', role_page='1'):
    """
    角色添加视图，带添加预览功能！
    """
    page_title = u'添加角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
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
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def role_delete(request, template_name='my.html', next='/', role_page='1',):
    """
    角色删除视图
    """
    page_title = u'删除角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
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
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def role_modify(request, template_name='my.html', next='/', role_page='1',):
    """
    角色修改视图
    """
    page_title = u'修改角色'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
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
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
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
                    query_set = Role.objects.filter(Q(is_active = True) & 
                                                           Q(name__startswith=role_search_form.cleaned_data['role_name']))
                else:
                    role_search_form.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
                    query_set = Role.objects.filter(Q(is_active = True) &
                                                       Q(name__icontains=role_search_form.cleaned_data['role_name']))
            else:
                query_set = Role.objects.filter(Q(is_active = True))

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
#       print data['is_fuzzy']

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
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def role_permission_add(request, template_name='my.html', next='/', role_permission_page='1', role_index='1',):
    """
    角色权限添加视图，带添加预览功能！
    """
    page_title = u'关联权限'
    user = get_user(request)

    try:
        role = Role.objects.get(is_active=True, pk=int(role_index))
    except:
        raise Http404('search form error!')

    department_query_set = Department.objects.filter(is_active=True)
    query_set_choices = department_query_set.exclude(department_to_role__role__pk=role.pk,
                                                     department_to_role__is_active=True)
    choices = ()
    for query in query_set_choices:
#        print str(query.pk), query.name
        choices += (str(query.pk), query.name),

    
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加关联':
            role_permission_add_form = RolePermissionAddForm(post_data)
            role_permission_add_form.fields['role_permission_name'].choices = choices
            if role_permission_add_form.is_valid():
                role_permission_add_form.role_permission_add(role)
                query_set_choices = department_query_set.exclude(department_to_role__role__pk=role.pk,
                                                     department_to_role__is_active=True)
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
                query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                             department_to_role__is_active=True)
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
                    query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                                 department_to_role__is_active=True)
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
            results_page = pagination_results(role_permission_page, query_set, settings.role_permission_PER_PAGE)
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
            query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                         department_to_role__is_active=True)
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
            results_page = pagination_results(role_permission_page, query_set, settings.role_permission_PER_PAGE)
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
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def role_permission_delete(request, template_name='my.html', next='/', role_permission_page='1', role_index='1',):
    """
    角色权限删除视图，带添加预览功能！
    """
    page_title = u'关联权限'

    try:
        role = Role.objects.get(is_active=True, pk=int(role_index))
    except:
        raise Http404('search form error!')

    department_query_set = Department.objects.filter(is_active=True)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
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
                query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                             department_to_role__is_active=True)
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
                    query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                                 department_to_role__is_active=True)
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
            results_page = pagination_results(role_permission_page, query_set, settings.role_permission_PER_PAGE)
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
            query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                         department_to_role__is_active=True)
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
            results_page = pagination_results(role_permission_page, query_set, settings.role_permission_PER_PAGE)
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
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def role_permission_list(request, template_name='my.html', next='/', role_permission_page='1', role_index='1',):
    """
    角色权限列表视图，带添加预览功能！
    """
    page_title = u'显示关联权限列表'

    try:
        role = Role.objects.get(is_active=True, pk=int(role_index))
    except:
        raise Http404('search form error!')

    department_query_set = Department.objects.filter(is_active=True)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        role_permission_search_form = RolePermissionSearchForm(post_data)
        if role_permission_search_form.is_valid():
            role_permission_search_form.save_to_session(request)
            query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                         department_to_role__is_active=True)
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
            results_page = pagination_results(role_permission_page, query_set, settings.role_permission_PER_PAGE)
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
        role_permission_search_form = RoleDepartmentSearchForm(data)
        if role_permission_search_form.is_valid():
            query_set_temp = department_query_set.filter(department_to_role__role__pk=role.pk,
                                                         department_to_role__is_active=True)
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
            results_page = pagination_results(role_department_page, query_set, settings.role_permission_PER_PAGE)
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
