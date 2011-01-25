#coding=utf-8

from __future__ import division

import chinese #主要是为了解决ReportLab中文bug

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import navy, yellow, red
from geraldo.generators import PDFGenerator
from django.http import HttpResponse
from django.core.cache import cache

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, BAND_WIDTH, landscape, Line

from hchq.check_project.models import CheckProject
from hchq.check_object.models import CheckObject
from hchq.check_result.models import CheckResult
from hchq.service_area.models import *
from django.db.models import ObjectDoesNotExist

from hchq.untils import gl
def get_check_count(instance=None):
    if instance is None:
        return u''
    
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department__service_area=instance).count()
    return u'%s' % check_count
def get_not_check_count(instance=None):
    if instance is None:
        return u''
    
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department__service_area=instance).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department__service_area=instance).count()
    if check_object_count > check_count:
        not_check_count = check_object_count - check_count
    else:
        not_check_count = 0

    return u'%s' % not_check_count


def get_check_object_count(instance=None):
    if instance is None:
        return u''

    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department__service_area=instance).count()

    return u'%s' % check_object_count

def get_total_count(value=None):
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).count()
    
    if check_object_count > check_count:
        not_check_count = check_object_count - check_count
        complete_radio = (check_count / check_object_count) * 100.0
    else:
        not_check_count = 0
        if check_object_count == 0:
            return u'检查项目：%s | 总已检人数：%s | 总未检人数：%s | 总人数：%s | 总完成度：------' % (check_project.name, check_count, not_check_count, check_object_count)
        else:
            complete_radio = 100.00

    return u'检查项目：%s | 总已检人数：%s | 总未检人数：%s | 总人数：%s | 总完成度：%.2f%%' % (check_project.name, check_count, not_check_count, check_object_count, complete_radio)            
    

def get_complete_radio(instance=None):
    if instance is None:
        return u''
    
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department__service_area=instance).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department__service_area=instance).count()
    if check_object_count > check_count:
        complete_radio = (check_count / check_object_count) * 100.0
    else:
        if check_object_count == 0:
            return u'------'
        else:
            complete_radio = 100.00

    return u'%.2f%%' % complete_radio

class CheckProjectReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),
            Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                  style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                  get_value=lambda text: get_total_count(text)),
            Line(left=0, top=1.6*cm, right=27.7*cm, bottom=1.6*cm, stroke_color=navy),
            Label(text=u"编号", top=1.8*cm, left=0.5*cm),
            Label(text=u"服务区域", top=1.8*cm, left=3.5*cm),
            Label(text=u"已检人数", top=1.8*cm, left=9.5*cm),
            Label(text=u"未检人数", top=1.8*cm, left=14.5*cm),
            Label(text=u"总人数", top=1.8*cm, left=19.5*cm),
            Label(text=u"完成度", top=1.8*cm, left=24.5*cm),
        ]
        borders = {'bottom': Line(stroke_color=navy)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s %(now:%H:%M)s创建。', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
            SystemField(expression = u'页号 %(page_number)d / %(page_count)d', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': Line(stroke_color=red)}

    class band_detail(ReportBand):
        height = 0.7*cm
        auto_expand_height = True
        elements = [
            ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
            ObjectValue(attribute_name='name', top=0.2*cm, left=3.5*cm),
            ObjectValue(attribute_name='name', top=0.2*cm, left=9.5*cm,
                        get_value=lambda instance: get_check_count(instance)),
            ObjectValue(attribute_name='name', top=0.2*cm, left=14.5*cm,
                        get_value=lambda instance: get_not_check_count(instance)),
            ObjectValue(attribute_name='name', top=0.2*cm, left=19.5*cm,
                        get_value=lambda instance: get_check_object_count(instance)),
            ObjectValue(attribute_name='name', top=0.2*cm, left=24.5*cm,
                        get_value=lambda instance: get_complete_radio(instance)),

            ]


def get_service_area_total_count(value=None, service_area=None):
    if service_area is None:
        return u''
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department__service_area=service_area).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department__service_area=service_area).count()
    
    if check_object_count > check_count:
        not_check_count = check_object_count - check_count
        complete_radio = (check_count / check_object_count) * 100.0
    else:
        not_check_count = 0
        if check_object_count == 0:
            return u'检查项目：%s | 总已检人数：%s | 总未检人数：%s | 总人数：%s | 总完成度：------' % (check_project.name, check_count, not_check_count, check_object_count)
        else:
            complete_radio = 100.00

    return u'检查项目：%s | 总已检人数：%s | 总未检人数：%s | 总人数：%s | 总完成度：%.2f%%' % (check_project.name, check_count, not_check_count, check_object_count, complete_radio)

def get_department_check_count(instance=None):
    if instance is None:
        return u''
    
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department=instance).count()
    return u'%s' % check_count
def get_department_not_check_count(instance=None):
    if instance is None:
        return u''
    
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department=instance).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department=instance).count()
    if check_object_count > check_count:
        not_check_count = check_object_count - check_count
    else:
        not_check_count = 0

    return u'%s' % not_check_count


def get_department_check_object_count(instance=None):
    if instance is None:
        return u''

    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department=instance).count()

    return u'%s' % check_object_count

def get_department_complete_radio(instance=None):
    if instance is None:
        return u''
    
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department=instance).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department=instance).count()
    if check_object_count > check_count:
        complete_radio = (check_count / check_object_count) * 100.0
    else:
        if check_object_count == 0:
            return u'------'
        else:
            complete_radio = 100.00

    return u'%.2f%%' % complete_radio

def get_department_name(instance=None):
    if instance is None:
        return u''
    return u'%s' % instance.department.name
    

class ServiceAreaReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),
            Line(left=0, top=1.6*cm, right=27.7*cm, bottom=1.6*cm, stroke_color=navy),
            Label(text=u"编号", top=1.8*cm, left=0.5*cm),
            Label(text=u"单位名称", top=1.8*cm, left=3.5*cm),
            Label(text=u"已检人数", top=1.8*cm, left=9.5*cm),
            Label(text=u"未检人数", top=1.8*cm, left=14.5*cm),
            Label(text=u"总人数", top=1.8*cm, left=19.5*cm),
            Label(text=u"完成度", top=1.8*cm, left=24.5*cm),
        ]
        borders = {'bottom': Line(stroke_color=navy)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s %(now:%H:%M)s创建。', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
            SystemField(expression = u'页号 %(page_number)d / %(page_count)d', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': Line(stroke_color=red)}

    class band_detail(ReportBand):
        height = 0.7*cm
        auto_expand_height = True
        elements = [
            ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
            ObjectValue(attribute_name='id', top=0.2*cm, left=3.5*cm,
                        get_value=lambda instance: get_department_name(instance)),
            ObjectValue(attribute_name='id', top=0.2*cm, left=9.5*cm,
                        get_value=lambda instance: get_department_check_count(instance)),
            ObjectValue(attribute_name='id', top=0.2*cm, left=14.5*cm,
                        get_value=lambda instance: get_department_not_check_count(instance)),
            ObjectValue(attribute_name='id', top=0.2*cm, left=19.5*cm,
                        get_value=lambda instance: get_department_check_object_count(instance)),
            ObjectValue(attribute_name='id', top=0.2*cm, left=24.5*cm,
                        get_value=lambda instance: get_department_complete_radio(instance)),

            ]

def get_department_total_count(value=None, service_area_department=None):
    if service_area_department is None:
        return u''
    check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    check_object_count = CheckObject.objects.filter(is_active=True).filter(service_area_department=service_area_department).count()
    check_count = CheckResult.objects.filter(is_latest=True, check_project=check_project).filter(check_object__service_area_department=service_area_department).count()
    
    if check_object_count > check_count:
        not_check_count = check_object_count - check_count
        complete_radio = (check_count / check_object_count) * 100.0
    else:
        not_check_count = 0
        if check_object_count == 0:
            return u'检查项目：%s | 总已检人数：%s | 总未检人数：%s | 总人数：%s | 总完成度：------' % (check_project.name, check_count, not_check_count, check_object_count)
        else:
            complete_radio = 100.00

    return u'检查项目：%s | 总已检人数：%s | 总未检人数：%s | 总人数：%s | 总完成度：%.2f%%' % (check_project.name, check_count, not_check_count, check_object_count, complete_radio)

def get_ctp_value(instance=None):
    if instance is not None and gl.check_object_ctp_local.has_key(instance.ctp_method):
        return u'%s' % gl.check_object_ctp_local[instance.ctp_method]
    else:
        return u''

class DepartmentReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.9*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 15, 'alignment': TA_CENTER, 'textColor': navy}),
            Line(left=0, top=1.6*cm, right=27.7*cm, bottom=1.6*cm, stroke_color=navy),
            Label(text=u"编号", top=2.0*cm, left=0.5*cm),
            Label(text=u"妻子姓名", top=1.8*cm, left=2*cm),
            Label(text=u"身份证号", top=2.2*cm, left=2*cm),
            Label(text=u"服务区域", top=1.8*cm, left=6.2*cm),
            Label(text=u"部门单位", top=2.2*cm, left=6.2*cm),
            Label(text=u"丈夫姓名", top=1.8*cm, left=12*cm),
            Label(text=u"身份证号", top=2.2*cm, left=12*cm),
            Label(text=u"服务区域", top=1.8*cm, left=16.2*cm),
            Label(text=u"部门单位", top=2.2*cm, left=16.2*cm),
            Label(text=u"是否家属", top=1.8*cm, left=22*cm),
            Label(text=u"结婚时间", top=2.2*cm, left=22*cm),
            Label(text=u"避孕措施", top=1.8*cm, left=25*cm),
            Label(text=u"实施时间", top=2.2*cm, left=25*cm),

        ]
        borders = {'bottom': Line(stroke_color=navy)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s %(now:%H:%M)s创建。', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
            SystemField(expression = u'页号 %(page_number)d / %(page_count)d', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': Line(stroke_color=red)}

    class band_detail(ReportBand):
        height = 0.7*cm
        auto_expand_height = True
        elements = [
            ObjectValue(attribute_name='id', top=0.3*cm, left=0.5*cm),
            ObjectValue(attribute_name='name', top=0.1*cm, left=2*cm),
            ObjectValue(attribute_name='id_number', top=0.5*cm, left=2*cm),
            ObjectValue(attribute_name='service_area_department.service_area.name', top=0.1*cm, left=6.2*cm),
            ObjectValue(attribute_name='service_area_department.department.name', top=0.5*cm, left=6.2*cm),
            ObjectValue(attribute_name='mate_name', top=0.1*cm, left=12*cm),
            ObjectValue(attribute_name='mate_id_number', top=0.5*cm, left=12*cm),
            ObjectValue(attribute_name='mate_service_area_department.service_area.name', top=0.1*cm, left=16.2*cm),
            ObjectValue(attribute_name='mate_service_area_department.department.name', top=0.5*cm, left=16.2*cm),
            ObjectValue(attribute_name='is_family', top=0.1*cm, left=22*cm,
                        get_value=lambda instance: instance.is_family and u'是' or u'否'),
            ObjectValue(attribute_name='wedding_time', top=0.5*cm, left=22*cm),
            ObjectValue(attribute_name='ctp_method', top=0.1*cm, left=25*cm,
                        get_value=lambda instance: get_ctp_value(instance)),
            ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
            ]

class CoverReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2*cm
        elements = [
            Line(left=0, top=0.5*cm, right=27.7*cm, bottom=0.5*cm, stroke_color=navy),
            SystemField(expression='%(report_title)s', top=8*cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 30, 'alignment': TA_CENTER, 'textColor': navy}),
            
        ]

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s %(now:%H:%M)s创建。', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
        ]
        borders = {'top': Line(stroke_color=red)}


def check_project_report(query_set=None, request=None):    
    if request.user.has_perm('department.unlocal'):
        response = cache.get('check_project_report_unlocal')
        if response is not None:
            return response
    else:
        response = cache.get('check_project_report_%s' % request.user.id)
        if response is not None:
            return response
    response = HttpResponse(mimetype='application/pdf')
    try:
        check_project = CheckProject.objects.get(is_setup=True, is_active=True)
    except ObjectDoesNotExist:
        return response
    
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        if request.user.has_perm('department.unlocal'):
            check_project_report = CheckProjectReport(query_set)
            check_project_report.author = request.user.username
            canvas = check_project_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
#        check_project_report.generate_by(PDFGenerator, filename=response)
            query_set_service_area = ServiceArea.objects.filter(is_active=True).order_by('id')
        else:
            cover_report = CoverReport(query_set)
            cover_report.author = request.user.username
            cover_report.title = u'%s' % check_project.name
            canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
            user_service_area_name = request.user.get_profile().service_area_department.service_area.name
            query_set_service_area = ServiceArea.objects.filter(is_active=True, name=user_service_area_name)
            
        for service_area_object in query_set_service_area:
            query_set_service_area_department = ServiceAreaDepartment.objects.filter(service_area = service_area_object, is_active=True)
            service_area_report = ServiceAreaReport(query_set_service_area_department)
            service_area_report.author = request.user.username
            service_area_report.title = u'%s-检查项目统计报表' % service_area_object.name
            service_area_report.band_page_header.elements += [
                Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                      style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                      get_value=lambda text: get_service_area_total_count(text, service_area=service_area_object)),
                ]
            canvas = service_area_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            for service_area_department_object in query_set_service_area_department:
                query_set_not_check_object_in_department = CheckObject.objects.filter(is_active=True).filter(service_area_department=service_area_department_object).exclude(check_result__is_latest=True, check_result__check_project=check_project)
                if query_set_not_check_object_in_department:
                    department_report = DepartmentReport(query_set_not_check_object_in_department)
                    department_report.author = request.user.username
                    department_report.title = u'%s-%s-未检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                    department_report.band_page_header.elements += [
                        Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: get_department_total_count(text, service_area_department=service_area_department_object)),
                        ]
                    canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        pass

    if request.user.has_perm('department.unlocal'):
        cache.set('check_project_report_unlocal', response, 15*60)
    else:
        cache.set('check_project_report_%s' % request.user.id, response, 15*60)

    return response
