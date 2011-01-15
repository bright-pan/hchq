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

class UserReport(Report):
    title = u'系统用户报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),     #这个地方的fontName设置属性似乎已经没有效果了！
            Line(left=0, top=1.4*cm, right=27.7*cm, bottom=1.4*cm, stroke_color=navy),
            Label(text=u"编号", top=1.7*cm, left=0.5*cm),
            Label(text=u"用户名称", top=1.7*cm, left=3.5*cm),
            Label(text=u"服务区域", top=1.5*cm, left=7.5*cm),
            Label(text=u"部门单位", top=1.9*cm, left=7.5*cm),
            Label(text=u"角色权限", top=1.7*cm, left=16.5*cm),
            Label(text=u"检查人员", top=1.7*cm, left=21.5*cm),
            Label(text=u"登入时间", top=1.5*cm, left=23.7*cm),
            Label(text=u"创建时间", top=1.9*cm, left=23.7*cm),
            
        ]
        borders = {'bottom': Line(stroke_color=navy)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s 创建。', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
            SystemField(expression = u'页号 %(page_number)d / %(page_count)d', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': Line(stroke_color=red)}

    class band_detail(ReportBand):
        height = 0.7*cm
        auto_expand_height = True
        elements = [
            ObjectValue(attribute_name='user.id', top=0.3*cm, left=0.5*cm),
            ObjectValue(attribute_name='user.username', top=0.3*cm, left=3.5*cm),
            ObjectValue(attribute_name='service_area_department.service_area.name', top=0.1*cm, left=7.5*cm),
            ObjectValue(attribute_name='service_area_department.department.name', top=0.5*cm, left=7.5*cm),
            ObjectValue(attribute_name='user.groups.get', top=0.3*cm, left=16.5*cm),
            ObjectValue(attribute_name='is_checker', top=0.3*cm, left=21.5*cm,
                        get_value=lambda instance: instance.is_checker and u'是' or u'否'),
            ObjectValue(attribute_name='user.last_login', top=0.1*cm, left=23.7*cm),
            ObjectValue(attribute_name='user.date_joined', top=0.5*cm, left=23.7*cm),
            ]

def user_report(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = UserReport(query_set)
        report.author = request.user.username
        report.generate_by(PDFGenerator, filename=response)

    else:
        pass
    return response
