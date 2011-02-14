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

class CheckProjectReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),
            Line(left=0, top=1.6*cm, right=27.7*cm, bottom=1.6*cm, stroke_color=navy),
            Label(text=u"编号", top=1.8*cm, left=0.5*cm),
            Label(text=u"考勤对象", top=1.8*cm, left=3.5*cm),
            Label(text=u"所属科室", top=1.8*cm, left=9.5*cm),
            Label(text=u"加班天数(天)", top=1.8*cm, left=14.5*cm),
            Label(text=u"加班次数", top=1.8*cm, left=19.5*cm),
            Label(text=u"加班工资(元)", top=1.8*cm, left=24.5*cm),
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
            ObjectValue(attribute_name='department_name', top=0.2*cm, left=9.5*cm),
            ObjectValue(attribute_name='check_result_days', top=0.2*cm, left=14.5*cm),
            ObjectValue(attribute_name='check_result_counts', top=0.2*cm, left=19.5*cm),
            ObjectValue(attribute_name='profit', top=0.2*cm, left=24.5*cm),

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

    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    
    if query_set is not None and request is not None and query_set:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'江西省会昌县人口与计划生育委员会考勤综合报表'
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        check_project_report = CheckProjectReport(query_set)
        check_project_report.author = request.user.username
        check_project_report.title = u'加班统计报表'
        canvas = check_project_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'考勤综合数据报表'
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport([{'name':u''}])
        cover_report.author = request.user.username
        cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    return response

