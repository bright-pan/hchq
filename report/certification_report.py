#coding=utf-8
#file name is SimpleListReport.py
import chinese #主要是为了解决ReportLab中文bug
import os
cur_dir = os.path.dirname(os.path.abspath(__file__))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import navy, yellow, red
from geraldo.generators import PDFGenerator
from django.http import HttpResponse

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, BAND_WIDTH, landscape, Line, Image

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
    
def get_name(instance = None):
    if instance is not None:
        if instance.is_family is True:
            return u'妻子姓名：%s|家属' % instance.name
        else:
            return u'妻子姓名：%s' % instance.name
    else:
        return u''
    
def get_id_number(instance = None):
    if instance is not None:
        return u'身份证号：%s' % instance.id_number
    else:
        return u''
def get_mate_name(instance = None):
    if instance is not None:
        return u'丈夫姓名：%s' % instance.mate_name
    else:
        return u''
def get_mate_id_number(instance = None):
    if instance is not None:
        return u'身份证号：%s' % instance.mate_id_number
    else:
        return u''

def get_service_area_department(instance=None):
    if instance is not None:
        return u'所属单位：%s %s' % (instance.service_area_department.service_area.name, instance.service_area_department.department.name)
    else:
        return u''    
def get_mate_service_area_department(instance=None):
    if instance is not None:
        return u'所属单位：%s %s' % (instance.mate_service_area_department.service_area.name, instance.mate_service_area_department.department.name)
    else:
        return u''

def get_result(instance=None):
    if instance is not None:
        result_object = instance.check_result.get(is_latest=True)
        value_list = result_object.result.split()
        if gl.check_result_local.has_key(value_list[0]) and gl.check_result_local.has_key(value_list[1]) and len(value_list) == 3:
            if value_list[2] == u'None':
                return u'%s|%s' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]])
            else:
                return u'%s|%s|%s周' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]], value_list[2])
        else:
            return u''
    else:
        return u''

def get_checker(instance=None):
    if instance is not None:
        result_object = instance.check_result.get(is_latest=True)
        return u'%s' % result_object.checker.username
    else:
        return u''
def get_check_service_area_department(instance=None):
    if instance is not None:
        result_object = instance.check_result.get(is_latest=True)
        service_area_department_object = result_object.checker.get_profile().service_area_department
        return u'%s %s' % (service_area_department_object.service_area.name, service_area_department_object.department.name)
    else:
        return u''

def get_check_time(instance=None):
    if instance is not None:
        result_object = instance.check_result.get(is_latest=True)
        return u'%s' % result_object.check_time
    else:
        return u''

class CertificationReport(Report):
    title = u'江西省会昌县环孕检证明'
#    page_size = landscape(A4)
    margin_top = 0
    margin_bottom = 0
    margin_left = 0
    margin_right = 0
    class band_page_header(ReportBand):
        height = 0
        elements = [
            Image(left=0, top=0,filename=os.path.join(cur_dir, 'bg.jpg')),
            Image(left=5.6*cm, top=2*cm, width=1.5*cm, height=1.5*cm,
                  filename=os.path.join(cur_dir, 'logo.jpg')),
            Line(left=1*cm, top=14.7*cm, right=2*cm, bottom=14.7*cm, stroke_width=3),
            Line(left=4*cm, top=14.7*cm, right=5*cm, bottom=14.7*cm, stroke_width=3),
            Line(left=7*cm, top=14.7*cm, right=8*cm, bottom=14.7*cm, stroke_width=3),
            Line(left=10*cm, top=14.7*cm, right=11*cm, bottom=14.7*cm, stroke_width=3),
            Line(left=13*cm, top=14.7*cm, right=14*cm, bottom=14.7*cm, stroke_width=3),
            Line(left=16*cm, top=14.7*cm, right=17*cm, bottom=14.7*cm, stroke_width=3),
            Line(left=19*cm, top=14.7*cm, right=20*cm, bottom=14.7*cm, stroke_width=3),
            Image(left=0, top=15.5*cm,filename=os.path.join(cur_dir, 'bg.jpg')),
            Image(left=5.6*cm, top=17.5*cm, width=1.5*cm, height=1.5*cm,
                  filename=os.path.join(cur_dir, 'logo.jpg')),
            SystemField(expression='%(report_title)s', top=2*cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER}),     #这个地方的fontName设置属性似乎已经没有效果了！
            
            SystemField(expression='%(report_title)s', top=17.5*cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 20, 'alignment': TA_CENTER}),     #这个地方的fontName设置属性似乎已经没有效果了！
        ]

    class band_detail(ReportBand):
        height = 0.7*cm
        auto_expand_height = True
        photo_path = u''


def certification_report(query_set=None, request=None):
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    if query_set is not None and request is not None and query_set:
        report = CertificationReport(query_set)
        query_object = query_set[0]
#        print query_object.photo.path
        report.band_detail.elements = [
            Image(left=14*cm, top=4*cm, width=7.5*cm, height=5.5*cm,
                  filename=query_object.photo.path),
            ObjectValue(attribute_name='name', top=4*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_name(instance)),
            ObjectValue(attribute_name='id_number', top=4.5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_id_number(instance)),
            ObjectValue(attribute_name='name', top=5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_service_area_department(instance)),
            ObjectValue(attribute_name='mate_name', top=6*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_mate_name(instance)),
            ObjectValue(attribute_name='mate_id_number', top=6.5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_mate_id_number(instance)),
            ObjectValue(attribute_name='name', top=7*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_mate_service_area_department(instance)),
            Label(text=u'_______________于________________________进行环孕检，检查人员 ____________ 对此人进行检查的检查结果为 _______________________，检查单位为_____________________________。',
                  top=8*cm, left=3*cm, width=15*cm),
            ObjectValue(attribute_name='name', top=8*cm, left=1.6*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},),
            ObjectValue(attribute_name='name', top=8*cm, left=5*cm,width=4*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_check_time(instance)),
            ObjectValue(attribute_name='name', top=8*cm, left=11.5*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_checker(instance)),
            ObjectValue(attribute_name='name', top=8.45*cm, left=3.5*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_result(instance)),
            ObjectValue(attribute_name='name', top=8.45*cm, left=4.5*cm,width=10*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_check_service_area_department(instance)),
            Label(text=u'检查人员：______________',
                  top=9.7*cm, left=9*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 10, 'alignment': TA_RIGHT},),
            Label(text=u'出具日期：______________',
                  top=9.7*cm, left=13.2*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 10, 'alignment': TA_RIGHT},),
            Label(text=u'(本证明检查单位盖章有效)',
                  top=10.5*cm, left=12*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 10, 'alignment': TA_RIGHT},),
            Label(text=u'(本证明一式两份，本份由检查对象保存。)',
                  top=12*cm, left=7.7*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 6, 'alignment': TA_CENTER},),
            
            Image(left=14*cm, top=19.5*cm, width=7.5*cm, height=5.5*cm,
                  filename=query_object.photo.path),
            ObjectValue(attribute_name='name', top=19.5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_name(instance)),
            ObjectValue(attribute_name='id_number', top=20*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_id_number(instance)),
            ObjectValue(attribute_name='name', top=20.5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_service_area_department(instance)),
            ObjectValue(attribute_name='mate_name', top=21.5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_mate_name(instance)),
            ObjectValue(attribute_name='mate_id_number', top=22*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_mate_id_number(instance)),
            ObjectValue(attribute_name='name', top=22.5*cm, left=3*cm,width=10*cm,
                        get_value=lambda instance: get_mate_service_area_department(instance)),
            Label(text=u'_______________于________________________进行环孕检，检查人员 ____________ 对此人进行检查的检查结果为 _______________________，检查单位为_____________________________。',
                  top=23.5*cm, left=3*cm, width=15*cm),
            ObjectValue(attribute_name='name', top=23.5*cm, left=1.6*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},),
            ObjectValue(attribute_name='name', top=23.5*cm, left=5*cm,width=4*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_check_time(instance)),
            ObjectValue(attribute_name='name', top=23.5*cm, left=11.5*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_checker(instance)),
            ObjectValue(attribute_name='name', top=23.95*cm, left=3.5*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_result(instance)),
            ObjectValue(attribute_name='name', top=23.95*cm, left=4.5*cm,width=10*cm,
                        style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_check_service_area_department(instance)),
            Label(text=u'检查人员：______________',
                  top=25.2*cm, left=9*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 10, 'alignment': TA_RIGHT},),
            Label(text=u'出具日期：______________',
                  top=25.2*cm, left=13.2*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 10, 'alignment': TA_RIGHT},),
            Label(text=u'(本证明检查单位盖章有效)',
                  top=26*cm, left=12*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 10, 'alignment': TA_RIGHT},),
            Label(text=u'(本证明一式两份，本份由检查单位保存。)',
                  top=27.5*cm, left=7.7*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 6, 'alignment': TA_CENTER},),

#            ObjectValue(attribute_name='name', top=7.5*cm, left=3*cm,width=15*cm,
#                        get_value=lambda instance: get_result(instance)),
            ]
#        print report.band_detail.elements
        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response
