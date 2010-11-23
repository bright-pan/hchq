#coding=utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
def my_layout_test(request, template_name = 'my.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))

def login(request, template_name = 'my.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))

def logout(request, template_name = 'my.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))
