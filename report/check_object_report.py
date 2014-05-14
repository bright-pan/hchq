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

from untils import gl
def get_ctp_value(instance=None):
    if instance is not None and gl.check_object_ctp_local.has_key(instance.ctp_method):
        return u'%s' % gl.check_object_ctp_local[instance.ctp_method]
    else:
        return u''


class CheckObjectReport(Report):
    title = u'检查对象报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),     #这个地方的fontName设置属性似乎已经没有效果了！
            Line(left=0, top=1.4*cm, right=27.7*cm, bottom=1.4*cm, stroke_color=navy),
            Label(text=u"编号", top=1.7*cm, left=0.5*cm),
            Label(text=u"妻子姓名", top=1.5*cm, left=2*cm),
            Label(text=u"身份证号", top=1.9*cm, left=2*cm),
            Label(text=u"服务区域", top=1.5*cm, left=6.2*cm),
            Label(text=u"部门单位", top=1.9*cm, left=6.2*cm),
            Label(text=u"丈夫姓名", top=1.5*cm, left=12*cm),
            Label(text=u"身份证号", top=1.9*cm, left=12*cm),
            Label(text=u"服务区域", top=1.5*cm, left=16.2*cm),
            Label(text=u"部门单位", top=1.9*cm, left=16.2*cm),
            Label(text=u"是否家属", top=1.5*cm, left=22*cm),
            Label(text=u"结婚时间", top=1.9*cm, left=22*cm),
            Label(text=u"避孕措施", top=1.5*cm, left=25*cm),
            Label(text=u"实施时间", top=1.9*cm, left=25*cm),
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

def check_object_report(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = CheckObjectReport(query_set)
        report.author = request.user.username
        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response

def check_object_unreport(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = CheckObjectReport(query_set)
        report.title = u'已删对象报表'
        report.author = request.user.username
        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response
