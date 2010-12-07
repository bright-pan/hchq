#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError

from hchq.department.models import Department
from hchq.untils import gl
import re

class DepartmentAddForm(forms.Form):
    """
    部门单位添加表单
    """
    department_name_set = None
    department_name = forms.CharField(
        max_length=500,
        required=True, 
        label=_(u'部门单位名称'), 
        widget=forms.Textarea(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：县委/政法委，公安局，...'),
        error_messages = gl.department_name_error_messages,
        )
    
    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
#            print department_name_copy
            if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
                raise forms.ValidationError(gl.department_name_error_messages['format_error'])
            self.department_name_set = set(filter(gl.filter_null_string, department_name_copy.split(u'/')))
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        return self.department_name_set

    def department_add(self, user=None):
        department_name_list = []
        department_name_obj = None
        created = None
        if user is not None and user.is_authenticated() and self.department_name_set is not None:
            for department_name_copy in self.department_name_set:
                department_name_obj, created = Department.objects.get_or_create(name=department_name_copy, creater=user)
                if created is True:
                    department_name_list.append(department_name_obj)
                else:
                    if department_name_obj.is_active == False:
                        department_name_obj.is_active = True
                        department_name_obj.save()
        return department_name_list

class DepartmentModifyForm(forms.Form):
    """
    部门单位修改表单
    """
    department_name_copy = None
    department_id_copy = None
    department_object = None
    department_id_object = None

    department_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'新部门单位名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.department_name_error_messages,
        )
    department_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.department_name_error_messages,
        )
    
    def clean_department_name(self):
        try:
            self.department_name_copy = self.data.get('department_name')
            try:
                self.department_id_copy = int(self.data.get('department_id'))
            except ValueError:
                raise forms.ValidationError(gl.department_name_error_messages['form_error'])
            self.department_id_object = Department.objects.get(pk=self.department_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
#            print self.department_name_copy
#            print type(self.department_id_copy)
        if re.match(gl.department_name_modify_re_pattern, self.department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            self.department_object = Department.objects.get(name=self.department_name_copy)
        except ObjectDoesNotExist:
            self.department_object = None
            return self.department_name_copy
        if self.department_object.id == self.department_id_copy:
            raise forms.ValidationError(gl.department_name_error_messages['already_error'])
        else:
            if self.department_object.is_active is True:
                raise forms.ValidationError(gl.department_name_error_messages['already_error'])
        return self.department_name_copy

    def department_modify(self):

        if self.department_object is not None:
            if self.department_object.is_active is False:
                self.department_object.is_active = True
                self.department_object.save()
                self.department_id_object.is_active = False
                self.department_id_object.save()
                return True
            else:
                return False
        else:
            self.department_id_object.name = self.department_name_copy
            self.department_id_object.save()
            return True

class DepartmentDeleteForm(forms.Form):
    """
    部门单位删除表单
    """
    department_id_copy = None
    department_id_object = None

    department_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.department_name_error_messages,
        )
    
    def clean_department_id(self):
        try:
            try:
                self.department_id_copy = int(self.data.get('department_id'))
            except ValueError:
                raise forms.ValidationError(gl.department_name_error_messages['form_error'])
            self.department_id_object = Department.objects.get(pk=self.department_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        return self.department_id_copy

    def department_delete(self):

        if self.department_id_object is not None:
            self.department_id_object.is_active = False
            self.department_id_object.save()
        else:
            return False

class DepartmentSearchForm(forms.Form):
    """
    部门单位搜索表单
    """
    department_name_copy = None
    is_fuzzy_value = None
    
    department_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'部门单位名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：县委，政法委...'),
        error_messages = gl.department_name_error_messages,
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'fuzzy_search',}, check_test=None),
        )
    
    def clean_department_name(self):
        try:
            self.department_name_copy = self.data.get('department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, self.department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
#        print self.department_name_copy
        return self.department_name_copy
    
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
        if self.department_name_copy == u'':
            return True
        else:
            return False
    def save_to_session(self, request):
        request.session[gl.session_department_name] = self.department_name_copy
        if self.fuzzy_search():
            request.session[gl.session_department_is_fuzzy] = u'fuzzy_search'
        else:
            request.session[gl.session_department_is_fuzzy] = False
        return True
