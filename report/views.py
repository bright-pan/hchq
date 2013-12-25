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

from check_project.models import CheckProject
from service_area.models import ServiceArea
from report.forms import *
from report.check_project_report import check_project_report

@csrf_protect
@login_required
@permission_required('department.cr_report')
#@permission_required('department.unlocal')
def report_statistics(request, template_name='my.html', next='/', ):
    """
    检查项目数据统计
    """
    page_title = u'检查项目数据统计'
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'生成项目报表':
            report_statistics_form = ReportStatisticsForm(post_data)
            report_statistics_form.init_check_project()
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
        report_statistics_form.init_check_project()
        return render_to_response(template_name,
                                  {'report_form': report_statistics_form,
                                   'page_title': page_title,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
@permission_required('department.cr_report')
def report_check_or_not(request, template_name='my.html', next='/', ):
    """
    检查项目数据统计
    """
    page_title = u'检查对象数据统计'
    user = get_user(request)
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data.get(u'submit', False)
        if submit_value == u'已检人员':
            report_check_or_not_form = ReportCheckOrNotForm(post_data)
            report_check_or_not_form.init_check_project()
            report_check_or_not_form.init_permission(user)
            if report_check_or_not_form.is_valid():
                return report_check_or_not_form.check_report(request)
            else:
                return render_to_response(template_name,
                                          {'report_form': report_check_or_not_form,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
        else:
            if submit_value == u'未检人员':
                report_check_or_not_form = ReportCheckOrNotForm(post_data)
                report_check_or_not_form.init_check_project()
                report_check_or_not_form.init_permission(user)
                if report_check_or_not_form.is_valid():
                    return report_check_or_not_form.not_report(request)
                else:
                    return render_to_response(template_name,
                                              {'report_form': report_check_or_not_form,
                                               'page_title': page_title,
                                               },
                                              context_instance=RequestContext(request))
            else:
                if submit_value == u'有孕人员':
                    report_check_or_not_form = ReportCheckOrNotForm(post_data)
                    report_check_or_not_form.init_check_project()
                    report_check_or_not_form.init_permission(user)
                    if report_check_or_not_form.is_valid():
                        return report_check_or_not_form.has_pregnant_report(request)
                    else:
                        return render_to_response(template_name,
                                              {'report_form': report_check_or_not_form,
                                               'page_title': page_title,
                                               },
                                              context_instance=RequestContext(request))
                else:
                    if submit_value == u'特殊检查人员':
                        report_check_or_not_form = ReportCheckOrNotForm(post_data)
                        report_check_or_not_form.init_check_project()
                        report_check_or_not_form.init_permission(user)
                        if report_check_or_not_form.is_valid():
                            return report_check_or_not_form.has_special_report(request)
                        else:
                            return render_to_response(template_name,
                                                      {'report_form': report_check_or_not_form,
                                                       'page_title': page_title,
                                                       },
                                                      context_instance=RequestContext(request))
                    else:
                        raise Http404('Invalid Request!')                
    else:
        report_check_or_not_form = ReportCheckOrNotForm()
        report_check_or_not_form.init_check_project()
        report_check_or_not_form.init_permission(user)
        return render_to_response(template_name,
                                  {'report_form': report_check_or_not_form,
                                   'page_title': page_title,
                                   },
                                  context_instance=RequestContext(request))
