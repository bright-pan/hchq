#coding=utf-8
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test

from account.forms import LoginForm,ModifyPasswordForm

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
def modify_password(request, template_name = '', next = '/'):
    
    page_title = u'修改密码'
    post_data = None
    modify_password_form = None
    if request.method == 'POST':
        post_data = request.POST.copy()
        modify_password_form = ModifyPasswordForm(post_data)
        if modify_password_form.is_valid():
            from django.contrib.auth import get_user            
            modify_password_form.password_save(get_user(request))
            return HttpResponseRedirect(next)
        else:
            return render_to_response(template_name, {'form': modify_password_form, 'page_title': page_title}, context_instance=RequestContext(request))
    else:
        modify_password_form = ModifyPasswordForm()
        return render_to_response(template_name, {'form': modify_password_form, 'page_title': page_title}, context_instance=RequestContext(request))        
