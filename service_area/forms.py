#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError

from hchq.service_area.models import ServiceArea, ServiceAreaDepartment
from hchq.department.models import Department
from hchq.untils import gl
import re

class ServiceAreaAddForm(forms.Form):
    """
    服务区域添加表单
    """
    service_area_name_set = None
    service_area_name = forms.CharField(
        max_length=500,
        required=True, 
        label=_(u'服务区域名称'), 
        widget=forms.Textarea(attrs={'class':'',
                                     'size':'30',
                                     'rows':'3',
                                     }
                              ), 
        help_text=_(u'例如：周田，周田乡/西江镇...'),
        error_messages = gl.service_area_name_error_messages,
        )
    
    def clean_service_area_name(self):
        try:
            service_area_name_copy = self.data.get('service_area_name')
#            print service_area_name_copy
            if re.match(gl.service_area_name_add_re_pattern, service_area_name_copy) is None:
                raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
            self.service_area_name_set = set(filter(gl.filter_null_string, service_area_name_copy.split(u'/')))
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
        return self.service_area_name_set

    def service_area_add(self, user=None):
        service_area_name_list = []
        service_area_name_obj = None
        created = None
        if user is not None and user.is_authenticated() and self.service_area_name_set is not None:
            for service_area_name_copy in self.service_area_name_set:
                service_area_name_obj, created = ServiceArea.objects.get_or_create(name=service_area_name_copy, creater=user)
                if created is True:
                    service_area_name_list.append(service_area_name_obj)
                else:
                    if service_area_name_obj.is_active == False:
                        service_area_name_obj.is_active = True
                        service_area_name_obj.save()
        return service_area_name_list

class ServiceAreaModifyForm(forms.Form):
    """
    服务区域修改表单
    """
    service_area_name_copy = None
    service_area_id_copy = None
    service_area_object = None
    service_area_id_object = None

    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'新服务区域名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    service_area_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.service_area_name_error_messages,
        )
    
    def clean_service_area_name(self):
        try:
            self.service_area_name_copy = self.data.get('service_area_name')
            try:
                self.service_area_id_copy = int(self.data.get('service_area_id'))
            except ValueError:
                raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
            self.service_area_id_object = ServiceArea.objects.get(pk=self.service_area_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
#            print self.service_area_name_copy
#            print type(self.service_area_id_copy)
        if re.match(gl.service_area_name_modify_re_pattern, self.service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
        try:
            self.service_area_object = ServiceArea.objects.get(name=self.service_area_name_copy)
        except ObjectDoesNotExist:
            self.service_area_object = None
            return self.service_area_name_copy
        if self.service_area_object.id == self.service_area_id_copy:
            raise forms.ValidationError(gl.service_area_name_error_messages['already_error'])
        else:
            if self.service_area_object.is_active is True:
                raise forms.ValidationError(gl.service_area_name_error_messages['already_error'])
        return self.service_area_name_copy

    def service_area_modify(self):

        if self.service_area_object is not None:
            if self.service_area_object.is_active is False:
                self.service_area_object.is_active = True
                self.service_area_object.save()
                self.service_area_id_object.is_active = False
                self.service_area_id_object.save()
                return True
            else:
                return False
        else:
            self.service_area_id_object.name = self.service_area_name_copy
            self.service_area_id_object.save()
            return True

class ServiceAreaDeleteForm(forms.Form):
    """
    服务区域删除表单
    """
    service_area_id_copy = None
    service_area_id_object = None

    service_area_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.service_area_name_error_messages,
        )
    
    def clean_service_area_id(self):
        try:
            try:
                self.service_area_id_copy = int(self.data.get('service_area_id'))
            except ValueError:
                raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
            self.service_area_id_object = ServiceArea.objects.get(pk=self.service_area_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
        return self.service_area_id_copy

    def service_area_delete(self):

        if self.service_area_id_object is not None:
            self.service_area_id_object.is_active = False
            self.service_area_id_object.save()
            ServiceAreaDepartment.objects.filter(service_area=self.service_area_id_object).update(is_active=True)
        else:
            return False

class ServiceAreaSearchForm(forms.Form):
    """
    服务区域搜索表单
    """
    service_area_name_copy = None
    is_fuzzy_value = None
    
    service_area_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'服务区域名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'fuzzy_search',}, check_test=None),
        )
    
    def clean_service_area_name(self):
        try:
            self.service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
        if re.match(gl.service_area_name_search_re_pattern, self.service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
#        print self.service_area_name_copy
        return self.service_area_name_copy
    
    def clean_is_fuzzy(self):
        try:
            self.is_fuzzy_value = self.data.get('is_fuzzy')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
#        print self.is_fuzzy_value
        return self.is_fuzzy_value
    
    def fuzzy_search(self):
        if self.is_fuzzy_value == u'fuzzy_search':
            return True
        else:
            return False
        
    def is_null(self):
        if self.service_area_name_copy == u'':
            return True
        else:
            return False
    def save_to_session(self, request):
        request.session[gl.session_service_area_name] = self.service_area_name_copy
        if self.fuzzy_search():
            request.session[gl.session_service_area_is_fuzzy] = u'fuzzy_search'
        else:
            request.session[gl.session_service_area_is_fuzzy] = False
        return True

class ServiceAreaDepartmentAddForm(forms.Form):
    """
    单位部门添加表单
    """
    service_area_department_name_set = None
    service_area_department_name = forms.MultipleChoiceField(
        required=True,
        label=_(u'单位部门名称'), 
        widget=forms.SelectMultiple( attrs={'class':'',
                                           'size':'30',},
                                    ), 
        help_text=_(u'帮助：按住键盘Ctrl键为多选！'),
        error_messages = gl.department_name_error_messages,
        )

    def service_area_department_add(self, service_area=None):
        service_area_department_name_copy = self.cleaned_data.get('service_area_department_name')
#        print type(service_area_department_name_copy)
        service_area_department_name_obj = None
        created = None
        if service_area is not None:
            for item in service_area_department_name_copy:
                try:
                    department_id = int(item)
                except ValueError:
                    return False
                try:
                    department = Department.objects.get(pk=department_id, is_active=True)
                except ObjectDoesNotExist:
                    return False
                service_area_department_name_obj, created = ServiceAreaDepartment.objects.get_or_create(service_area=service_area, department=department)
                if created is True:
                    pass
                else:
                    if service_area_department_name_obj.is_active == False:
                        service_area_department_name_obj.is_active = True
                        service_area_department_name_obj.save()
        return True

class ServiceAreaDepartmentSearchForm(forms.Form):
    """
    单位部门搜索表单
    """
    service_area_department_name_copy = None
    is_fuzzy_value = None
    
    service_area_department_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'单位部门名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',
                                      }
                               ), 
        help_text=_(u'例如：县委，政法委...'),
        error_messages = gl.department_name_error_messages,
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'fuzzy_search',
                                          }, 
                                   check_test=None,
                                   ),
        )
    
    def clean_service_area_department_name(self):
        try:
            self.service_area_department_name_copy = self.data.get('service_area_department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, self.service_area_department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
#        print self.service_area_department_name_copy
        return self.service_area_department_name_copy
    
    def clean_is_fuzzy(self):
        try:
            self.is_fuzzy_value = self.data.get('is_fuzzy')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
#        print self.is_fuzzy_value
        return self.is_fuzzy_value
    
    def fuzzy_search(self):
        if self.is_fuzzy_value == u'fuzzy_search':
            return True
        else:
            return False
        
    def is_null(self):
        if self.service_area_department_name_copy == u'':
            return True
        else:
            return False
    def save_to_session(self, request):
        request.session[gl.session_service_area_department_name] = self.service_area_department_name_copy
        if self.fuzzy_search():
            request.session[gl.session_service_area_department_is_fuzzy] = u'fuzzy_search'
        else:
            request.session[gl.session_service_area_department_is_fuzzy] = False
        return True

class ServiceAreaDepartmentDeleteForm(forms.Form):
    """
    单位部门删除表单
    """
    service_area_department_id_copy = None

    service_area_department_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.department_name_error_messages,
        )
    
    def clean_service_area_department_id(self):
        try:
            try:
                self.service_area_department_id_copy = int(self.data.get('service_area_department_id'))
            except ValueError:
                raise forms.ValidationError(gl.service_area_department_name_error_messages['form_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_department_name_error_messages['form_error'])
        return self.service_area_department_id_copy

    def service_area_department_delete(self, service_area=None):

        if service_area is not None and self.service_area_department_id_copy is not None:
            try:
                service_area_department_id_object = ServiceAreaDepartment.objects.get(service_area=service_area, department__id = self.service_area_department_id_copy)
            except ObjectDoesNotExist:
                return False
            service_area_department_id_object.is_active = False
            service_area_department_id_object.save()
            return True
        return False
