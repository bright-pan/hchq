#% -*- coding: utf-8 -*-
#coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q

from hchq.report.forms import *
from hchq.report.check_project_report import check_project_report

@csrf_protect
@login_required
def report_statistics(request, template_name='my.html', next='/', ):
    """
    检查项目数据统计
    """
    page_title = u'检查项目数据统计'
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'生成统计报表':
            report_statistics_form = ReportStatisticsForm(post_data)
            if report_statistics_form.is_valid():
                return report_statistics_form.report(request)
            else:
                return render_to_response(template_name,
                                          {'report_form': report_statistics_form,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
        else:
            raise Http404('Invalid Request!')                
    else:
        report_statistics_form = ReportStatisticsForm()
        return render_to_response(template_name,
                                  {'report_form': report_statistics_form,
                                   'page_title': page_title,
                                   },
                                  context_instance=RequestContext(request))

