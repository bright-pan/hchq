#coding=utf-8
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user
from hchq.account.forms import LoginForm,ModifyPasswordForm

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
