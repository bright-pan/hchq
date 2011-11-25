#coding=utf-8

from __future__ import division

import chinese #主要是为了解决ReportLab中文bug
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import navy, yellow, red
from geraldo.generators import PDFGenerator
from django.http import HttpResponse
from django.core.cache import cache
from django.db.models import Avg, Max, Min, Count

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, BAND_WIDTH, landscape, Line

from hchq.check_project.models import CheckProject
from hchq.check_object.models import CheckObject
from hchq.check_result.models import CheckResult
from hchq.service_area.models import *
from hchq.report.check_result_report import CheckResultReport
from django.db.models import ObjectDoesNotExist

from hchq.untils import gl

class CheckProjectReport(Report):
    title = u'江西省会昌县环孕检统计报表'
    page_size = landscape(A4)
    check_project = None
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),
            Line(left=0, top=1.6*cm, right=27.7*cm, bottom=1.6*cm, stroke_color=navy),
            Label(text=u"编号", top=1.8*cm, left=0.5*cm),
            Label(text=u"服务区域", top=1.8*cm, left=3.5*cm),
            Label(text=u"已检人数(有孕|特殊)", top=1.8*cm, left=9.5*cm),
            Label(text=u"未检人数", top=1.8*cm, left=14.5*cm),
            Label(text=u"总人数", top=1.8*cm, left=19.5*cm),
            Label(text=u"完成度", top=1.8*cm, left=24.5*cm),
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

    def get_check_count(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_result = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department__service_area=instance)
        check_count = check_result.aggregate(Count('check_object', distinct=True))['check_object__count']
        pregnant_count = check_result.filter(result__startswith='pregnant').aggregate(Count('check_object', distinct=True))['check_object__count']
        special_count = check_result.filter(result__startswith='special').aggregate(Count('check_object', distinct=True))['check_object__count']
        return u'%s(%s|%s)' % (check_count, pregnant_count, special_count)

    def get_not_check_count(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23, 59, 59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department__service_area=instance).count()
        check_count = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department__service_area=instance).aggregate(Count('check_object', distinct=True))['check_object__count']
        if check_object_count > check_count:
            not_check_count = check_object_count - check_count
        else:
            not_check_count = 0
        return u'%s' % not_check_count

    def get_check_object_count(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department__service_area=instance).count()

        return u'%s' % check_object_count

    def get_total_count(self, value=None):
        if self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).count()

        check_result = CheckResult.objects.filter(check_project=self.check_project)
        check_count = check_result.aggregate(Count('check_object', distinct=True))['check_object__count']
        pregnant_count = check_result.filter(result__startswith='pregnant').aggregate(Count('check_object', distinct=True))['check_object__count']
        special_count = check_result.filter(result__startswith='special').aggregate(Count('check_object', distinct=True))['check_object__count']
        if check_object_count > check_count:
            not_check_count = check_object_count - check_count
            complete_radio = (check_count / check_object_count) * 100.0
        else:
            not_check_count = 0
            if check_object_count == 0:
                return u'检查项目：%s | 总已检人数(有孕|特殊)：%s(%s|%s) | 总未检人数：%s | 总人数：%s | 总完成度：------' % (check_project.name,
                                                                                                                         check_count,
                                                                                                                         pregnant_count,
                                                                                                                         special_count,
                                                                                                                         not_check_count,
                                                                                                                         check_object_count)
            else:
                complete_radio = 100.00
        return u'检查项目：%s | 总已检人数(有孕|特殊)：%s(%s|%s) | 总未检人数：%s | 总人数：%s | 总完成度：%.2f%%' % (self.check_project.name,
                                                                                                                 check_count,
                                                                                                                 pregnant_count,
                                                                                                                 special_count,
                                                                                                                 not_check_count,
                                                                                                                 check_object_count,
                                                                                                                 complete_radio)     
    

    def get_complete_radio(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23, 59, 59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department__service_area=instance).count()

        check_count = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department__service_area=instance).aggregate(Count('check_object', distinct=True))['check_object__count']
        if check_object_count > check_count:
            complete_radio = (check_count / check_object_count) * 100.0
        else:
            if check_object_count == 0:
                return u'------'
            else:
                complete_radio = 100.00
        return u'%.2f%%' % complete_radio

    

class ServiceAreaReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    check_project = None
    class band_page_header(ReportBand):
        height = 2.5*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER, 'textColor': navy}),
            Line(left=0, top=1.6*cm, right=27.7*cm, bottom=1.6*cm, stroke_color=navy),
            Label(text=u"编号", top=1.8*cm, left=0.5*cm),
            Label(text=u"单位名称", top=1.8*cm, left=3.5*cm),
            Label(text=u"已检人数(有孕|特殊)", top=1.8*cm, left=9.5*cm),
            Label(text=u"未检人数", top=1.8*cm, left=14.5*cm),
            Label(text=u"总人数", top=1.8*cm, left=19.5*cm),
            Label(text=u"完成度", top=1.8*cm, left=24.5*cm),
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
        check_result = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department__service_area=service_area)
        check_count = check_result.aggregate(Count('check_object', distinct=True))['check_object__count']
        pregnant_count = check_result.filter(result__startswith='pregnant').aggregate(Count('check_object', distinct=True))['check_object__count']
        special_count = check_result.filter(result__startswith='special').aggregate(Count('check_object', distinct=True))['check_object__count']
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

    def get_department_check_count(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_result = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department=instance)
        check_count = check_result.aggregate(Count('check_object', distinct=True))['check_object__count']
        pregnant_count = check_result.filter(result__startswith='pregnant').aggregate(Count('check_object', distinct=True))['check_object__count']
        special_count = check_result.filter(result__startswith='special').aggregate(Count('check_object', distinct=True))['check_object__count']
        return u'%s(%s|%s)' % (check_count, pregnant_count, special_count)

    def get_department_not_check_count(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department=instance).count()

        check_count = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department=instance).aggregate(Count('check_object', distinct=True))['check_object__count']
        if check_object_count > check_count:
            not_check_count = check_object_count - check_count
        else:
            not_check_count = 0

        return u'%s' % not_check_count


    def get_department_check_object_count(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department=instance).count()
        return u'%s' % check_object_count

    def get_department_complete_radio(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        check_project_endtime = datetime.datetime(self.check_project.end_time.year,
                                                   self.check_project.end_time.month,
                                                   self.check_project.end_time.day,
                                                   23,
                                                   59,
                                                   59)
        check_object_count = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                       updated_at__lt=check_project_endtime,
                                                                                                       ).filter(service_area_department=instance).count()
        check_count = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department=instance).aggregate(Count('check_object', distinct=True))['check_object__count']
        if check_object_count > check_count:
            complete_radio = (check_count / check_object_count) * 100.0
        else:
            if check_object_count == 0:
                return u'------'
            else:
                complete_radio = 100.00

        return u'%.2f%%' % complete_radio

    def get_department_name(self, instance=None):
        if instance is None or self.check_project is None:
            return u''
        return u'%s' % instance.department.name


class DepartmentReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    check_project = None
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
        check_result = CheckResult.objects.filter(check_project=self.check_project).filter(check_object__service_area_department=service_area_department).order_by('check_object.id')
        check_count = check_result.aggregate(Count('check_object', distinct=True))['check_object__count']
        pregnant_count = check_result.filter(result__startswith='pregnant').aggregate(Count('check_object', distinct=True))['check_object__count']    
        special_count = check_result.filter(result__startswith='special').aggregate(Count('check_object', distinct=True))['check_object__count']
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

    def get_ctp_value(self, instance=None):
        if instance is not None and gl.check_object_ctp_local.has_key(instance.ctp_method):
            return u'%s' % gl.check_object_ctp_local[instance.ctp_method]
        else:
            return u''

class CoverReport(Report):
    title = u'会昌县检查项目统计报表'
    page_size = landscape(A4)
    class band_page_header(ReportBand):
        height = 2*cm
        elements = [
            Line(left=0, top=0.5*cm, right=27.7*cm, bottom=0.5*cm, stroke_color=navy),
            SystemField(expression='%(report_title)s', top=9.5*cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 30, 'alignment': TA_CENTER, 'textColor': navy}),
            SystemField(expression=u'江 西 省 会 昌 县', top=7.5*cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 30, 'alignment': TA_CENTER, 'textColor': navy}),
            
        ]

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            SystemField(expression = u'由 %(report_author)s 于 %(now:%Y-%m-%d)s %(now:%H:%M)s创建', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            SystemField(expression = u'江西省会昌县人口与计划生育委员会', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
        ]
        borders = {'top': Line(stroke_color=red)}


def check_project_report(query_set=None, request=None, has_department_info=False, has_pregnant_info=False, has_special_info=False, has_check=False, has_not=False, check_project_id=None):
    response = cache.get('check_project_report_%s_%s_%s_%s_%s_%s_%s' % (request.user.id, check_project_id, has_department_info, has_pregnant_info, has_special_info, has_check, has_not))

    if response is not None:
        return response
    
    response = HttpResponse(mimetype='application/pdf')
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
            check_project_endtime = datetime.datetime(check_project.end_time.year,
                                                      check_project.end_time.month,
                                                      check_project.end_time.day,
                                                      23, 59, 59)
        except ObjectDoesNotExist:
            check_project = None
        
    else:
        check_project = None
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        if request.user.has_perm('department.unlocal'):
            check_project_report = CheckProjectReport(query_set)
            check_project_report.check_project = check_project
            check_project_report.author = request.user.username
            check_project_report.band_page_header.elements += [
                Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                      style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                      get_value=lambda text: check_project_report.get_total_count(text)),
                ]
            check_project_report.band_detail.elements = [
                ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
                ObjectValue(attribute_name='name', top=0.2*cm, left=3.5*cm),
                ObjectValue(attribute_name='name', top=0.2*cm, left=9.5*cm,
                            get_value=lambda instance: check_project_report.get_check_count(instance)),
                ObjectValue(attribute_name='name', top=0.2*cm, left=14.5*cm,
                            get_value=lambda instance: check_project_report.get_not_check_count(instance)),
                ObjectValue(attribute_name='name', top=0.2*cm, left=19.5*cm,
                            get_value=lambda instance: check_project_report.get_check_object_count(instance)),
                ObjectValue(attribute_name='name', top=0.2*cm, left=24.5*cm,
                            get_value=lambda instance: check_project_report.get_complete_radio(instance)),
                ]
            canvas = check_project_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
#        check_project_report.generate_by(PDFGenerator, filename=response)
            query_set_service_area = ServiceArea.objects.filter(is_active=True).order_by('id')
        else:
            user_service_area_name = request.user.get_profile().service_area_department.service_area.name
            query_set_service_area = ServiceArea.objects.filter(is_active=True, name=user_service_area_name)
            
        for service_area_object in query_set_service_area:
            query_set_service_area_department = ServiceAreaDepartment.objects.filter(service_area = service_area_object, is_active=True)
            if has_department_info is True:
                if query_set_service_area_department:
                    service_area_report = ServiceAreaReport(query_set_service_area_department)
                    service_area_report.check_project = check_project
                    service_area_report.author = request.user.username
                    service_area_report.title = u'%s - 环孕检统计报表' % service_area_object.name
                    service_area_report.band_page_header.elements += [
                        Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: service_area_report.get_service_area_total_count(text, service_area=service_area_object)),
                        ]
                    service_area_report.band_detail.elements = [
                        ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
                        ObjectValue(attribute_name='id', top=0.2*cm, left=3.5*cm,
                                    get_value=lambda instance: service_area_report.get_department_name(instance)),
                        ObjectValue(attribute_name='id', top=0.2*cm, left=9.5*cm,
                                    get_value=lambda instance: service_area_report.get_department_check_count(instance)),
                        ObjectValue(attribute_name='id', top=0.2*cm, left=14.5*cm,
                                    get_value=lambda instance: service_area_report.get_department_not_check_count(instance)),
                        ObjectValue(attribute_name='id', top=0.2*cm, left=19.5*cm,
                                    get_value=lambda instance: service_area_report.get_department_check_object_count(instance)),
                        ObjectValue(attribute_name='id', top=0.2*cm, left=24.5*cm,
                                    get_value=lambda instance: service_area_report.get_department_complete_radio(instance)),

                        ]

                    canvas = service_area_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
            else:
                pass
            if has_pregnant_info is True:
                query_set_check_result = CheckResult.objects.filter(check_project=check_project).filter(check_object__service_area_department__service_area=service_area_object).filter(result__startswith='pregnant').order_by(u'check_object__service_area_department__service_area__name').order_by('check_object.id')
                if query_set_check_result:
                    check_result_report = CheckResultReport(query_set_check_result)
                    check_result_report.check_project = check_project
                    check_result_report.author = request.user.username
                    check_result_report.title = u'%s - 有孕人员名单' % service_area_object.name
                    check_result_report.band_page_header.elements += [
                        Label(text=u'', top=1*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: check_result_report.get_service_area_total_count(text, service_area=service_area_object)),
                        ]
                    check_result_report.band_detail.elements = [
                        ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
                        ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                                    get_value=lambda instance: check_result_report.get_family_value(instance)),
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
                                    get_value=lambda instance: check_result_report.get_result_value(instance)),
                        ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
                        ]

                    canvas = check_result_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
            else:
                pass
            if has_special_info is True:
                query_set_check_result = CheckResult.objects.filter(check_project=check_project).filter(check_object__service_area_department__service_area=service_area_object).filter(result__startswith='special').order_by(u'check_object__service_area_department__service_area__name').order_by('check_object.id')
                if query_set_check_result:
                    check_result_report = CheckResultReport(query_set_check_result)
                    check_result_report.check_project = check_project
                    check_result_report.author = request.user.username
                    check_result_report.title = u'%s - 特殊检查名单' % service_area_object.name
                    check_result_report.band_page_header.elements += [
                        Label(text=u'', top=1*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: check_result_report.get_service_area_total_count(text, service_area=service_area_object)),
                        ]
                    check_result_report.band_detail.elements = [
                        ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
                        ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                                    get_value=lambda instance: check_result_report.get_family_value(instance)),
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
                                    get_value=lambda instance: check_result_report.get_result_value(instance)),
                        ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
                        ]

                    canvas = check_result_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
            else:
                pass            
            if has_check is True or has_not is True:
                for service_area_department_object in query_set_service_area_department:
                    if has_not is True:
                        query_set_not_check_object_in_department = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                                                             updated_at__lt=check_project_endtime,
                                                                                                                                             ).filter(service_area_department=service_area_department_object).exclude(check_result__check_project=check_project).order_by('id')
                        if query_set_not_check_object_in_department:
                            department_report = DepartmentReport(query_set_not_check_object_in_department)
                            department_report.check_project = check_project
                            department_report.author = request.user.username
                            department_report.title = u'%s - %s - 未检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                            department_report.band_page_header.elements += [
                                Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                                      style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                                      get_value=lambda text: department_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                                ]
                            department_report.band_detail.elements = [
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
                                            get_value=lambda instance: department_report.get_ctp_value(instance)),
                                ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
                                ]

                            canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                        else:
                            pass
                    if has_check is True:
                        query_set_check_object_in_department = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                                                             updated_at__lt=check_project_endtime,
                                                                                                                                             ).filter(service_area_department=service_area_department_object).filter(check_result__check_project=check_project).order_by('id')
                        if query_set_check_object_in_department:
                            department_report = DepartmentReport(query_set_check_object_in_department)
                            department_report.check_project = check_project
                            department_report.author = request.user.username
                            department_report.title = u'%s - %s - 已检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                            department_report.band_page_header.elements += [
                                Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                                      style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                                      get_value=lambda text: department_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                                ]
                            department_report.band_detail.elements = [
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
                                            get_value=lambda instance: department_report.get_ctp_value(instance)),
                                ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
                                ]
                            canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                        else:
                            pass
                    else:
                        pass
            else:
                pass
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_project_report_%s_%s_%s_%s_%s_%s_%s' % (request.user.id, check_project_id, has_department_info, has_pregnant_info, has_special_info, has_check, has_not), response, 15*60)
    return response

def check_object_check_service_area_report(query_set=None, request=None, check_project_id=None):

    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
            check_project_endtime = datetime.datetime(check_project.end_time.year,
                                                      check_project.end_time.month,
                                                      check_project.end_time.day,
                                                      23, 59, 59)

        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None

    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_check_service_area_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area = query_set
        for service_area_object in query_set_service_area:
            query_set_service_area_department = ServiceAreaDepartment.objects.filter(service_area = service_area_object, is_active=True)
            if query_set_service_area_department:
                service_area_report = ServiceAreaReport(query_set_service_area_department)
                service_area_report.check_project = check_project
                service_area_report.author = request.user.username
                service_area_report.title = u'%s - 环孕检统计报表' % service_area_object.name
                service_area_report.band_page_header.elements += [
                    Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: service_area_report.get_service_area_total_count(text, service_area=service_area_object)),
                    ]
                service_area_report.band_detail.elements = [
                    ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=3.5*cm,
                                get_value=lambda instance: service_area_report.get_department_name(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=9.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=14.5*cm,
                                get_value=lambda instance: service_area_report.get_department_not_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=19.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_object_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=24.5*cm,
                                get_value=lambda instance: service_area_report.get_department_complete_radio(instance)),

                    ]
                canvas = service_area_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            for service_area_department_object in query_set_service_area_department:
                query_set_not_check_object_in_department = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                                                     updated_at__lt=check_project_endtime,
                                                                                                                                     ).filter(service_area_department=service_area_department_object).filter(check_result__check_project=check_project).order_by('id')
                if query_set_not_check_object_in_department:
                    department_report = DepartmentReport(query_set_not_check_object_in_department)
                    department_report.check_project = check_project
                    department_report.author = request.user.username
                    department_report.title = u'%s - %s - 已检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                    department_report.band_page_header.elements += [
                        Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: department_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                        ]
                    department_report.band_detail.elements = [
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
                                    get_value=lambda instance: department_report.get_ctp_value(instance)),
                        ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
                        ]
                    canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_check_service_area_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response

def check_object_check_service_area_department_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
            check_project_endtime = datetime.datetime(check_project.end_time.year,
                                                      check_project.end_time.month,
                                                      check_project.end_time.day,
                                                      23, 59, 59)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None

    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_check_service_area_department_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area_department = query_set
        for service_area_department_object in query_set_service_area_department:
            query_set_not_check_object_in_department = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                                                     updated_at__lt=check_project_endtime,
                                                                                                                                     ).filter(service_area_department=service_area_department_object).filter(check_result__check_project=check_project).order_by('id')
            if query_set_not_check_object_in_department:
                department_report = DepartmentReport(query_set_not_check_object_in_department)
                department_report.check_project = check_project
                department_report.author = request.user.username
                department_report.title = u'%s - %s - 已检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                department_report.band_page_header.elements += [
                    Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: department_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                    ]
                department_report.band_detail.elements = [
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
                                get_value=lambda instance: department_report.get_ctp_value(instance)),
                    ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
                    ]
                canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_check_service_area_department_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response

def check_object_not_service_area_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
            check_project_endtime = datetime.datetime(check_project.end_time.year,
                                                      check_project.end_time.month,
                                                      check_project.end_time.day,
                                                      23, 59, 59)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None
        
    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_not_service_area_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area = query_set
        for service_area_object in query_set_service_area:
            query_set_service_area_department = ServiceAreaDepartment.objects.filter(service_area = service_area_object, is_active=True)
            if query_set_service_area_department:
                service_area_report = ServiceAreaReport(query_set_service_area_department)
                service_area_report.check_project = check_project
                service_area_report.author = request.user.username
                service_area_report.title = u'%s - 环孕检统计报表' % service_area_object.name
                service_area_report.band_page_header.elements += [
                    Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: service_area_report.get_service_area_total_count(text, service_area=service_area_object)),
                    ]
                service_area_report.band_detail.elements = [
                    ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=3.5*cm,
                                get_value=lambda instance: service_area_report.get_department_name(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=9.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=14.5*cm,
                                get_value=lambda instance: service_area_report.get_department_not_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=19.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_object_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=24.5*cm,
                                get_value=lambda instance: service_area_report.get_department_complete_radio(instance)),

                    ]
                canvas = service_area_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            for service_area_department_object in query_set_service_area_department:
                query_set_not_check_object_in_department = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                                                     updated_at__lt=check_project_endtime,
                                                                                                                                     ).filter(service_area_department=service_area_department_object).exclude(check_result__check_project=check_project).order_by('id')
                if query_set_not_check_object_in_department:
                    department_report = DepartmentReport(query_set_not_check_object_in_department)
                    department_report.check_project = check_project
                    department_report.author = request.user.username
                    department_report.title = u'%s - %s - 未检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                    department_report.band_page_header.elements += [
                        Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: department_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                        ]
                    department_report.band_detail.elements = [
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
                                    get_value=lambda instance: department_report.get_ctp_value(instance)),
                        ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
                        ]
                    canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_not_service_area_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response

def check_object_not_service_area_department_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
            check_project_endtime = datetime.datetime(check_project.end_time.year,
                                                      check_project.end_time.month,
                                                      check_project.end_time.day,
                                                      23, 59, 59)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None

    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_not_service_area_department_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area_department = query_set
        for service_area_department_object in query_set_service_area_department:
            query_set_not_check_object_in_department = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                                                     updated_at__lt=check_project_endtime,
                                                                                                                                     ).filter(service_area_department=service_area_department_object).exclude(check_result__check_project=check_project).order_by('id')
            if query_set_not_check_object_in_department:
                department_report = DepartmentReport(query_set_not_check_object_in_department)
                department_report.check_project = check_project
                department_report.author = request.user.username
                department_report.title = u'%s - %s - 未检人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                department_report.band_page_header.elements += [
                    Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: department_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                    ]
                department_report.band_detail.elements = [
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
                                get_value=lambda instance: department_report.get_ctp_value(instance)),
                    ObjectValue(attribute_name='ctp_method_time', top=0.5*cm, left=25*cm),
                    ]
                canvas = department_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_not_service_area_department_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response
def check_object_service_area_has_pregnant_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None
        
    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_service_area_has_pregnant_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area = query_set
        for service_area_object in query_set_service_area:
            query_set_service_area_department = ServiceAreaDepartment.objects.filter(service_area = service_area_object, is_active=True)
            if query_set_service_area_department:
                service_area_report = ServiceAreaReport(query_set_service_area_department)
                service_area_report.check_project = check_project
                service_area_report.author = request.user.username
                service_area_report.title = u'%s - 环孕检统计报表' % service_area_object.name
                service_area_report.band_page_header.elements += [
                    Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: service_area_report.get_service_area_total_count(text, service_area=service_area_object)),
                    ]
                service_area_report.band_detail.elements = [
                    ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=3.5*cm,
                                get_value=lambda instance: service_area_report.get_department_name(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=9.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=14.5*cm,
                                get_value=lambda instance: service_area_report.get_department_not_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=19.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_object_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=24.5*cm,
                                get_value=lambda instance: service_area_report.get_department_complete_radio(instance)),

                    ]
                canvas = service_area_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            for service_area_department_object in query_set_service_area_department:
                query_set_check_result_has_pregnant_in_department = CheckResult.objects.filter(check_project=check_project).filter(check_object__service_area_department=service_area_department_object).filter(result__startswith='pregnant', is_latest=True).order_by('check_object.id')
                if query_set_check_result_has_pregnant_in_department:
                    check_result_report = CheckResultReport(query_set_check_result_has_pregnant_in_department)
                    check_result_report.check_project = check_project
                    check_result_report.author = request.user.username
                    check_result_report.title = u'%s-%s-有孕人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                    check_result_report.band_page_header.elements += [
                        Label(text=u'', top=1*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: check_result_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                        ]
                    check_result_report.band_detail.elements = [
                        ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
                        ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                                    get_value=lambda instance: check_result_report.get_family_value(instance)),
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
                                    get_value=lambda instance: check_result_report.get_result_value(instance)),
                        ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
                        ]
                    canvas = check_result_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_service_area_has_pregnant_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response

def check_object_service_area_department_has_pregnant_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None

    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_service_area_department_has_pregnant_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area_department = query_set
        for service_area_department_object in query_set_service_area_department:
            query_set_check_result_has_pregnant_in_department = CheckResult.objects.filter(check_project=check_project).filter(check_object__service_area_department=service_area_department_object).filter(result__startswith='pregnant').order_by('check_object.id')
            if query_set_check_result_has_pregnant_in_department:
                check_result_report = CheckResultReport(query_set_check_result_has_pregnant_in_department)
                check_result_report.check_project = check_project
                check_result_report.author = request.user.username
                check_result_report.title = u'%s-%s-有孕人员名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                check_result_report.band_page_header.elements += [
                    Label(text=u'', top=1*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: check_result_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                    ]
                check_result_report.band_detail.elements = [
                    ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
                    ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                                get_value=lambda instance: check_result_report.get_family_value(instance)),
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
                                get_value=lambda instance: check_result_report.get_result_value(instance)),
                    ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
                    ]
                canvas = check_result_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_service_area_department_has_pregnant_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response
def check_object_service_area_has_special_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None
        
    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_service_area_has_special_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area = query_set
        for service_area_object in query_set_service_area:
            query_set_service_area_department = ServiceAreaDepartment.objects.filter(service_area = service_area_object, is_active=True)
            if query_set_service_area_department:
                service_area_report = ServiceAreaReport(query_set_service_area_department)
                service_area_report.check_project = check_project
                service_area_report.author = request.user.username
                service_area_report.title = u'%s - 环孕检统计报表' % service_area_object.name
                service_area_report.band_page_header.elements += [
                    Label(text=u'', top=1.2*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: service_area_report.get_service_area_total_count(text, service_area=service_area_object)),
                    ]
                service_area_report.band_detail.elements = [
                    ObjectValue(attribute_name='id', top=0.2*cm, left=0.5*cm),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=3.5*cm,
                                get_value=lambda instance: service_area_report.get_department_name(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=9.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=14.5*cm,
                                get_value=lambda instance: service_area_report.get_department_not_check_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=19.5*cm,
                                get_value=lambda instance: service_area_report.get_department_check_object_count(instance)),
                    ObjectValue(attribute_name='id', top=0.2*cm, left=24.5*cm,
                                get_value=lambda instance: service_area_report.get_department_complete_radio(instance)),

                    ]
                canvas = service_area_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            for service_area_department_object in query_set_service_area_department:
                query_set_check_result_has_special_in_department = CheckResult.objects.filter(check_project = check_project).filter(check_object__service_area_department=service_area_department_object).filter(result__startswith='special').order_by('check_object.id')
                if query_set_check_result_has_special_in_department:
                    check_result_report = CheckResultReport(query_set_check_result_has_special_in_department)
                    check_result_report.check_project = check_project
                    check_result_report.author = request.user.username
                    check_result_report.title = u'%s-%s-特殊检查名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                    check_result_report.band_page_header.elements += [
                        Label(text=u'', top=1*cm, left=0, width=BAND_WIDTH,
                              style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                              get_value=lambda text: check_result_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                        ]
                    check_result_report.band_detail.elements = [
                        ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
                        ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                                    get_value=lambda instance: check_result_report.get_family_value(instance)),
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
                                    get_value=lambda instance: check_result_report.get_result_value(instance)),
                        ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
                        ]
                    canvas = check_result_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
                else:
                    pass
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_service_area_has_special_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response

def check_object_service_area_department_has_special_report(query_set=None, request=None, check_project_id=None):
    
    if check_project_id is not None:
        try:
            check_project = CheckProject.objects.get(pk=check_project_id, is_active=True)
        except ObjectDoesNotExist:
            check_project = None
    else:
        check_project = None

    if query_set is not None and request is not None and query_set:
        response = cache.get('check_object_service_area_department_has_special_report_%s_%s' % (check_project_id, query_set[0].id))
        if response is not None:
            return response
        response = HttpResponse(mimetype='application/pdf')
        if check_project == None:
            return response
        
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        canvas = cover_report.generate_by(PDFGenerator, filename=response, return_canvas=True)
        query_set_service_area_department = query_set
        for service_area_department_object in query_set_service_area_department:
            query_set_check_result_has_special_in_department = CheckResult.objects.filter(check_project = check_project).filter(check_object__service_area_department=service_area_department_object).filter(result__startswith='special').order_by('check_object.id')
            if query_set_check_result_has_special_in_department:
                check_result_report = CheckResultReport(query_set_check_result_has_special_in_department)
                check_result_report.check_project = check_project
                check_result_report.author = request.user.username
                check_result_report.title = u'%s-%s-特殊检查名单' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
                check_result_report.band_page_header.elements += [
                    Label(text=u'', top=1*cm, left=0, width=BAND_WIDTH,
                          style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                          get_value=lambda text: check_result_report.get_department_total_count(text, service_area_department=service_area_department_object)),
                    ]
                check_result_report.band_detail.elements = [
                    ObjectValue(attribute_name='check_object.id', top=0.3*cm, left=0.5*cm),
                    ObjectValue(attribute_name='check_object.name', top=0.1*cm, left=2*cm,
                                get_value=lambda instance: check_result_report.get_family_value(instance)),
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
                                get_value=lambda instance: check_result_report.get_result_value(instance)),
                    ObjectValue(attribute_name='check_time', top=0.5*cm, left=24*cm),
                    ]
                canvas = check_result_report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
            else:
                pass
            cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        cover_report.title = u'%s' % check_project.name
        cover_report.generate_by(PDFGenerator, canvas=canvas)
        
    else:
        cover_report = CoverReport(query_set)
        cover_report.author = request.user.username
        if check_project is not None:
            cover_report.title = u'%s' % check_project.name
        else:
            cover_report.title = u'无效报表'
        cover_report.generate_by(PDFGenerator, filename=response)
        return response

    cache.set('check_object_service_area_department_has_special_report_%s_%s' % (check_project_id, query_set[0].id), response, 15*60)
    return response

