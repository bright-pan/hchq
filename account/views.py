#coding=utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from account.forms import login_form

# Create your views here.
def my_layout_test(request, template_name = 'my.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))

@csrf_protect
@never_cache
def login(request, template_name = 'account/login.html', next = '/'):

    page_title = u'用户登入'
    #loginform = login_form()
    if request.method == 'POST':
        loginform = login_form(request.POST)
        if loginform.is_valid():
            from django.contrib.auth import login
            login(request, loginform.get_user())
            return HttpResponseRedirect(next)
        else:
            return render_to_response(template_name, {'form': loginform, 'page_title': page_title}, context_instance=RequestContext(request))
    else:
        loginform = login_form()
        return render_to_response(template_name, {'form': loginform, 'page_title': page_title}, context_instance=RequestContext(request))

def exit(request, template_name = 'my.html', next = '/'):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect(next)
