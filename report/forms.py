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

    def check_report(self, request=None):
        if self.service_area_department_object is None:
            query_set = ServiceArea.objects.filter(name=self.cleaned_data['service_area_name'], is_active=True)
            return check_object_check_service_area_report(query_set, request)
        else:
            return check_object_check_service_area_department_report([self.service_area_department_object], request)

        return response

    def not_report(self, request=None):
        if self.service_area_department_object is None:
            query_set = ServiceArea.objects.filter(name=self.cleaned_data['service_area_name'], is_active=True)
            return check_object_not_service_area_report(query_set, request)
        else:
            return check_object_not_service_area_department_report([self.service_area_department_object], request)

        return response

    
class ReportStatisticsForm(forms.Form):
    pass
    
