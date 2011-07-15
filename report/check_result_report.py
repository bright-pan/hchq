#% -*- coding: utf-8 -*-
#coding=utf-8
#file name is SimpleListReport.py
import chinese #主要是为了解决ReportLab中文bug

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import navy, yellow, red
from geraldo.generators import PDFGenerator
from django.http import HttpResponse

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, BAND_WIDTH, landscape, Line

from hchq.untils import gl
def get_result_value(instance=None):
    if instance is None:
        return u''
    value_list = instance.result.split()
    if gl.check_result_local.has_key(value_list[0]) and gl.check_result_local.has_key(value_list[1]) and len(value_list) == 3:
        if value_list[2] == u'None':
            return u'%s|%s' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]])
        else:
            return u'%s|%s|%s周' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]], value_list[2])
    else:
        return u''

def get_family_value(instance = None):
    if instance is not None:
        temp_object = instance.check_object
        if temp_object.is_family is True:
            return u'%s|%s' % (temp_object.name, u'家属')
        else:
            return temp_object.name
    else:
        return u''
    
class CheckResultReport(Report):
    title = u'检查结果报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),     #这个地方的fontName设置属性似乎已经没有效果了！
            Line(left=0, top=1.4*cm, right=27.7*cm, bottom=1.4*cm, stroke_color=navy),
            Label(text=u"编号", top=1.7*cm, left=0.5*cm),
            Label(text=u"妻子姓名|家属", top=1.5*cm, left=2*cm),
            Label(text=u"身份证号", top=1.9*cm, left=2*cm),
            Label(text=u"服务区域", top=1.5*cm, left=6.2*cm),
            Label(text=u"部门单位", top=1.9*cm, left=6.2*cm),
            Label(text=u"丈夫姓名", top=1.5*cm, left=11.5*cm),
            Label(text=u"身份证号", top=1.9*cm, left=11.5*cm),
            Label(text=u"服务区域", top=1.5*cm, left=15.7*cm),
            Label(text=u"部门单位", top=1.9*cm, left=15.7*cm),
            Label(text=u"检查人员", top=1.5*cm, left=21*cm),
            Label(text=u"检查项目", top=1.9*cm, left=21*cm),
            Label(text=u"检查结果", top=1.5*cm, left=24*cm),
            Label(text=u"检查时间", top=1.9*cm, left=24*cm),
        ]
        borders = {'bottom': Line(stroke_color=navy)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s %(now:%H:%M)s创建', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            SystemField(expression = u'页号 %(page_number)d / %(page_count)d', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_CENTER}),
            SystemField(expression = u'江西省会昌县人口与计划生育委员会', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),

        ]
        borders = {'top': Line(stroke_color=red)}

    class band_detail(ReportBand):
        height = 0.7*cm
        auto_expand_height = True
        elements = [
            ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
            ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                        get_value=lambda instance: get_family_value(instance)),
            ObjectValue(attribute_name='check_object.id_number', top=0.5*cm, left=2*cm),
            ObjectValue(attribute_name='check_object.service_area_department.service_area.name', top=0.1*cm, left=6.2*cm),
            ObjectValue(attribute_name='check_object.service_area_department.department.name', top=0.5*cm, left=6.2*cm),
            ObjectValue(attribute_name='check_object.mate_name', top=0.1*cm, left=11.5*cm),
            ObjectValue(attribute_name='check_object.mate_id_number', top=0.5*cm, left=11.5*cm),
            ObjectValue(attribute_name='check_object.mate_service_area_department.service_area.name', top=0.1*cm, left=15.7*cm),
            ObjectValue(attribute_name='check_object.mate_service_area_department.department.name', top=0.5*cm, left=15.7*cm),
            ObjectValue(attribute_name='checker.username', top=0.1*cm, left=21*cm),
            ObjectValue(attribute_name='check_project.name', top=0.5*cm, left=21*cm, width=3*cm),
            ObjectValue(attribute_name='result', top=0.1*cm, left=24*cm,
                        get_value=lambda instance: get_result_value(instance)),
            ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
            ]

def check_result_report(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = CheckResultReport(query_set)
        report.author = request.user.username
        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response
