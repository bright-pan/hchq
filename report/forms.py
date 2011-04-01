#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist
from PIL import Image
from StringIO import StringIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from hchq.untils import gl
from hchq.service_area.models import ServiceArea, ServiceAreaDepartment
from hchq.department.models import Department
from hchq.check_project.models import CheckProject
from hchq.check_object.models import *
from hchq import settings
import re
import datetime

from hchq.report.check_project_report import *

class ReportCheckOrNotForm(forms.Form):
    
    service_area_department_object = None

    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域'),
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=False, 
        label=_(u'单位部门'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )
    check_project = forms.ChoiceField(
        required=True,
        label =_(u'检查项目(*)'),
        help_text=_(u'选择一个合适的检查项目'),
        )

    def clean_service_area_name(self):
        try:
           service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_add_re_pattern, service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        try:
            ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        return service_area_name_copy

    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
            service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        if department_name_copy == u'':
            return department_name_copy
        try:
            department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            service_area_object = ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.service_area_department_object = ServiceAreaDepartment.objects.get(service_area=service_area_object, department=department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return department_name_copy

    def clean_check_project(self):
        try:
           check_project_copy = self.data.get('check_project')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
        try:
            check_project_id = int(check_project_copy)
        except ValueError:
            raise forms.ValidationError(u'请选择一个正确检查项目')
        try:
            CheckProject.objects.get(pk=check_project_id, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(u'这个检查项目不存在')
        return check_project_id

    def init_permission(self, user=None):
        if user is not None:
            if user.has_perm('department.unlocal'):
                return False
            else:
                self.fields['service_area_name'].widget.attrs['value'] = user.get_profile().service_area_department.service_area.name
                self.fields['service_area_name'].widget.attrs['readonly'] = True
                return True
        else:
            return None

    def init_check_project(self):
        choices = ((u'none',u'未知'),)
        query_set = CheckProject.objects.filter(is_active=True)
        for query in query_set:
            choices += (str(query.pk), query.name),
        self.fields['check_project'].choices = choices

    def check_report(self, request=None):
        if self.service_area_department_object is None:
            query_set = ServiceArea.objects.filter(name=self.cleaned_data['service_area_name'], is_active=True)
            return check_object_check_service_area_report(query_set, request, self.cleaned_data['check_project'])
        else:
            return check_object_check_service_area_department_report([self.service_area_department_object], request, self.cleaned_data['check_project'])

        return response

    def not_report(self, request=None):
        if self.service_area_department_object is None:
            query_set = ServiceArea.objects.filter(name=self.cleaned_data['service_area_name'], is_active=True)
            return check_object_not_service_area_report(query_set, request, self.cleaned_data['check_project'])
        else:
            return check_object_not_service_area_department_report([self.service_area_department_object], request, self.cleaned_data['check_project'])

        return response

    
class ReportStatisticsForm(forms.Form):

    has_department_info = forms.CharField(
        required=True,
        label =_(u'单位统计'),
        help_text=_(u'打勾则对服务区域中的单位进行统计'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'has_department_info',
                                          }, 
                                   check_test=None,
                                   ),
        )

    has_check = forms.CharField(
        required=True,
        label =_(u'已检对象名单'),
        help_text=_(u'打勾则包含已检对象名单'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'has_check',
                                          }, 
                                   check_test=None,
                                   ),
        )
    has_not = forms.CharField(
        required=True,
        label =_(u'未检对象名单'),
        help_text=_(u'打勾则包含未检对象名单'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'has_not',
                                          }, 
                                   check_test=None,
                                   ),
        )
    check_project = forms.ChoiceField(
        required=True,
        label =_(u'检查项目(*)'),
        help_text=_(u'选择一个合适的检查项目'),
        )
    def clean_check_project(self):
        try:
           check_project_copy = self.data.get('check_project')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
        try:
            check_project_id = int(check_project_copy)
        except ValueError:
            raise forms.ValidationError(u'请选择一个正确检查项目')
        try:
            CheckProject.objects.get(pk=check_project_id, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(u'这个检查项目不存在')
        return check_project_id

    def init_check_project(self):
        choices = ((u'none',u'未知'),)
        query_set = CheckProject.objects.filter(is_active=True)
        for query in query_set:
            choices += (str(query.pk), query.name),
        self.fields['check_project'].choices = choices

    def report(self, request=None):
        if self.cleaned_data['has_department_info'] == u'has_department_info':
            has_department_info = True
        else:
            has_department_info = False
            
        if self.cleaned_data['has_check'] == u'has_check':
            has_check = True
        else:
            has_check = False
            
        if self.cleaned_data['has_not'] == u'has_not':
            has_not = True
        else:
            has_not = False
            
        query_set = ServiceArea.objects.filter(is_active=True).order_by('id')
        return check_project_report(query_set, request, has_department_info, has_check, has_not, self.cleaned_data['check_project'])
