#% -*- coding: utf-8 -*-
#coding=utf-8
#file name is SimpleListReport.py

from __future__ import division

import chinese #主要是为了解决ReportLab中文bug
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import navy, yellow, red
from geraldo.generators import PDFGenerator
from django.http import HttpResponse

from hchq.check_project.models import CheckProject
from hchq.check_object.models import CheckObject
from hchq.check_result.models import CheckResult

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, BAND_WIDTH, landscape, Line, Image

from hchq.untils import gl
    
class CheckResultReport(Report):
    title = u'检查结果报表'
    page_size = landscape(A4)
    check_project = None
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

    def get_result_value(self, instance=None):
        if instance is None:
            return u''
        value_list = instance.result.split()
#    print value_list
        value_len = len(value_list)
        if value_len == 3:
            if gl.check_result_local.has_key(value_list[0]) and gl.check_result_local.has_key(value_list[1]):
                if value_list[2] == u'None':
                    return u'%s|%s' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]])
                else:
                    return u'%s|%s|%s周' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]], value_list[2])
            else:
                return u'未知结果'
        else:
            if value_len == 1:
                if gl.check_result_local.has_key(value_list[0]):
                    return u'%s' % (gl.check_result_local[value_list[0]])
                else:
                    return u'未知结果'
            else:
                return u'未知结果'

    def get_family_value(self, instance = None):
        if instance is not None:
            temp_object = instance.check_object
            if temp_object.is_family is True:
                return u'%s|%s' % (temp_object.name, u'家属')
            else:
                return temp_object.name
        else:
            return u''

    def get_service_area_total_count(self, value=None, service_area=None):
        if service_area is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department__service_area=service_area).count()
        check_result = CheckResult.objects.filter(is_latest=True, check_project=self.check_project).filter(check_object__service_area_department__service_area=service_area)
        check_count = check_result.count()
        pregnant_count = check_result.filter(result__startswith='pregnant').count()    
        special_count = check_result.filter(result__startswith='special').count()    
        if check_object_count > check_count:
            not_check_count = check_object_count - check_count
            complete_radio = (check_count / check_object_count) * 100.0
        else:
            not_check_count = 0
            if check_object_count == 0:
                return u'检查项目：%s | 总已检人数(有孕|特殊)：%s(%s|%s) | 总未检人数：%s | 总人数：%s | 总完成度：------' % (self.check_project.name, check_count, pregnant_count, special_count, not_check_count, check_object_count)
            else:
                complete_radio = 100.00

        return u'检查项目：%s | 总已检人数(有孕|特殊)：%s(%s|%s) | 总未检人数：%s | 总人数：%s | 总完成度：%.2f%%' % (self.check_project.name, check_count, pregnant_count, special_count, not_check_count, check_object_count, complete_radio)            
    def get_department_total_count(self, value=None, service_area_department=None):
        if service_area_department is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department=service_area_department).count()
        check_result = CheckResult.objects.filter(is_latest=True, check_project=self.check_project).filter(check_object__service_area_department=service_area_department)
        check_count = check_result.count()
        pregnant_count = check_result.filter(result__startswith='pregnant').count()    
        special_count = check_result.filter(result__startswith='special').count()    
        if check_object_count > check_count:
            not_check_count = check_object_count - check_count
            complete_radio = (check_count / check_object_count) * 100.0
            print complete_radio, check_count, check_object_count
        else:
            not_check_count = 0
            if check_object_count == 0:
                return u'检查项目：%s | 总已检人数(有孕|特殊)：%s(%s|%s) | 总未检人数：%s | 总人数：%s | 总完成度：------' % (self.check_project.name, check_count, pregnant_count, special_count, not_check_count, check_object_count)
            else:
                complete_radio = 100.00

        return u'检查项目：%s | 总已检人数(有孕|特殊)：%s(%s|%s) | 总未检人数：%s | 总人数：%s | 总完成度：%.2f%%' % (self.check_project.name, check_count, pregnant_count, special_count, not_check_count, check_object_count, complete_radio)            

def check_result_report(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = CheckResultReport(query_set)
        report.author = request.user.username
        report.band_detail.elements = [
            ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),

            ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                        get_value=lambda instance: report.get_family_value(instance)),
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
                        get_value=lambda instance: report.get_result_value(instance)),
            ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
            ]

        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response
