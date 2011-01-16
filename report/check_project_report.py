#coding=utf-8

from __future__ import division

import chinese #主要是为了解决ReportLab中文bug

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import navy, yellow, red
from geraldo.generators import PDFGenerator
from django.http import HttpResponse

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, BAND_WIDTH, landscape, Line

from hchq.check_project.models import CheckProject
from hchq.check_object.models import CheckObject
from hchq.check_result.models import CheckResult
from hchq.service_area.models import ServiceArea


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
    title = u'检查项目统计报表'
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

def check_project_report(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = CheckProjectReport(query_set)
        report.author = request.user.username
        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response
