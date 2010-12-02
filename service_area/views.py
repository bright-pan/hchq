#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from hchq.service_area.forms import ServiceAreaAddForm
from hchq.service_area.models import ServiceArea
from hchq import settings
@csrf_protect
@user_passes_test(lambda u: u.is_authenticated(), login_url='/account/login')
def service_area_add(request, template_name='my.html', next='/'):

    page_title = u'添加服务区域'
    user = get_user(request)
    post_data = None
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    query_set = ServiceArea.objects.all()
    paginator = Paginator(query_set, settings.SERVICE_AREA_PER_PAGE)
    try:
        results_page = paginator.page(page)
    except (InvalidPage, EmptyPage):
        results_page = paginator.page(1)
    if request.method == 'POST':
        post_data = request.POST.copy()
        service_area_add_form = ServiceAreaAddForm(post_data)
        if service_area_add_form.is_valid():
            service_area_add_form.service_area_save(user)
            return render_to_response(template_name,
                                      {'form': service_area_add_form,
                                       'page_title': page_title,
                                       'results_page':results_page,
                                       },
                                      context_instance=RequestContext(request))
        else:
            return render_to_response(template_name,
                                      {'form': service_area_add_form,
                                       'page_title': page_title,
                                       'results_page':results_page,
                                       },
                                      context_instance=RequestContext(request))
    else:
        service_area_add_form = ServiceAreaAddForm()
        return render_to_response(template_name,
                                  {'form': service_area_add_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


