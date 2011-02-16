#coding=utf-8
#file name is SimpleListReport.py
import chinese #主要是为了解决ReportLab中文bug
import os
cur_dir = os.path.dirname(os.path.abspath(__file__))

from reportlab.lib.pagesizes import A6
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
            return u'%s(%s)' % (temp_object.name, u'家属')
        else:
            return temp_object.name
    else:
        return u''
    
def get_name(instance = None):
    if instance is not None:
        if instance.is_family is True:
            return u'妻子姓名：%s(家属)' % instance.name
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
    page_size = landscape(A6)
    margin_top = 0
    margin_bottom = 0
    margin_left = 0
    margin_right = 0
    class band_page_header(ReportBand):
        height = 0
        elements = [
            Image(left=0, top=0, width=26.2*cm, height=18.5*cm,
                  filename=os.path.join(cur_dir, 'bg.jpg')),
            SystemField(expression='%(report_title)s', top=1.5*cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'yahei', 'fontSize': 15, 'alignment': TA_CENTER}),     #这个地方的fontName设置属性似乎已经没有效果了！
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
            Image(left=9.2*cm, top=3*cm, width=6*cm, height=4.8*cm,
                  filename=query_object.photo.path),
            ObjectValue(attribute_name='name', top=3*cm, left=2.2*cm,width=7*cm,
                        style={'fontName': 'yahei', 'fontSize': 8},
                        get_value=lambda instance: get_name(instance)),
            ObjectValue(attribute_name='id_number', top=3.4*cm, left=2.2*cm,width=7*cm,
                        style={'fontName': 'yahei', 'fontSize': 8},
                        get_value=lambda instance: get_id_number(instance)),
            ObjectValue(attribute_name='name', top=3.8*cm, left=2.2*cm,width=7*cm,
                        style={'fontName': 'yahei', 'fontSize': 8},
                        get_value=lambda instance: get_service_area_department(instance)),
            ObjectValue(attribute_name='mate_name', top=4.6*cm, left=2.2*cm,width=7*cm,
                        style={'fontName': 'yahei', 'fontSize': 8},
                        get_value=lambda instance: get_mate_name(instance)),
            ObjectValue(attribute_name='mate_id_number', top=5.0*cm, left=2.2*cm,width=7*cm,
                        style={'fontName': 'yahei', 'fontSize': 8},
                        get_value=lambda instance: get_mate_id_number(instance)),
            ObjectValue(attribute_name='name', top=5.4*cm, left=2.2*cm,width=7*cm,
                        style={'fontName': 'yahei', 'fontSize': 8},
                        get_value=lambda instance: get_mate_service_area_department(instance)),
            Label(text=u'____________于________________________进行环孕检，检查人员 ____________ 对此人进行检查的检查结果为 __________________，检查单位为____________________________，检查单位联系电话___________________________________。',
                  top=6.4*cm, left=2.2*cm, width=10.5*cm, style={'fontName': 'yahei', 'fontSize': 8},),
            ObjectValue(attribute_name='name', top=6.4*cm, left=1.5*cm,width=1.5*cm,
                        style={'fontName': 'yahei', 'fontSize': 7, 'alignment': TA_RIGHT, 'textColor': red},),
            ObjectValue(attribute_name='name', top=6.4*cm, left=2.7*cm,width=4*cm,
                        style={'fontName': 'yahei', 'fontSize': 7, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_check_time(instance)),
            ObjectValue(attribute_name='name', top=6.4*cm, left=8.1*cm,width=3*cm,
                        style={'fontName': 'yahei', 'fontSize': 7, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_checker(instance)),
            ObjectValue(attribute_name='name', top=6.8*cm, left=2.6*cm,width=4*cm,
                        style={'fontName': 'yahei', 'fontSize': 7, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_result(instance)),
            ObjectValue(attribute_name='name', top=6.8*cm, left=2*cm,width=10*cm,
                        style={'fontName': 'yahei', 'fontSize': 7, 'alignment': TA_RIGHT, 'textColor': red},
                        get_value=lambda instance: get_check_service_area_department(instance)),
            Label(text=u'发证人员(签字)：______________',
                  top=8*cm, left=4.2*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT},),
            Label(text=u'发证日期：______________',
                  top=8*cm, left=7.5*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT},),
            Label(text=u'(本证明检查单位盖章有效)',
                  top=8.5*cm, left=7.5*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 8, 'alignment': TA_RIGHT},),
            Label(text=u'江西省会昌县人口与计划生育委员会监制',
                  top=9.55*cm, left=4.8*cm, width=5*cm,
                  style={'fontName': 'yahei', 'fontSize': 6, 'alignment': TA_CENTER},),
            
            ]
#        print report.band_detail.elements
        report.generate_by(PDFGenerator, filename=response)
    else:
        pass
    return response
