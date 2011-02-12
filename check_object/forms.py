#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from hchq.untils import gl
from hchq.department.models import Department
from hchq.check_object.models import *
from hchq import settings
import re
import datetime

class CheckObjectAddForm(forms.Form):
    """
    检查对象添加表单
    """

    department_object = None
    
    name = forms.CharField(
        max_length=64,
        required=True, 
        label=_(u'考勤对象姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'科室名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：综治办/政策法规股、政策法规股、'),
        error_messages = gl.department_name_error_messages,
        )
    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
            
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        try:
            check_object = CheckObject.objects.get(is_active=True, name=self.data['name'])
        except ObjectDoesNotExist:
            return name_copy
        raise forms.ValidationError(u'该对象姓名已经存在！')
        
    
    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            self.department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        return department_name_copy

    def add(self, user = None):
        if user is not None :
            try:
                check_object = CheckObject.objects.get(is_active=False, name=self.cleaned_data['name'])
            except ObjectDoesNotExist:
#                print self.cleaned_data['wedding_time'], self.cleaned_data['address']
                check_object, created = CheckObject.objects.get_or_create(name=self.cleaned_data['name'],
                                                          department=self.department_object,
                                                          creater = user,
                                                          )
                return check_object
            check_object.is_active =True
            check_object.name=self.cleaned_data['name']
            check_object.department=self.department_object
            check_object.creater = user
            check_object.save()
            return check_object
        return None
            

class CheckObjectModifyForm(forms.Form):
    """
    检查对象修改表单
    """

    id_object = None

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=True)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def object(self):
        return self.id_object

class CheckObjectDetailModifyForm(forms.Form):
    """
    检查对象详细修改表单
    """
    id_object = None
    department_object = None
    
    name = forms.CharField(
        max_length=64,
        required=True, 
        label=_(u'考勤对象姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )

    department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'科室名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：综治办/政策法规股、政策法规股、'),
        error_messages = gl.department_name_error_messages,
        )

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )

    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            self.department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        return department_name_copy

    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=True)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def data_from_object(self, modify_object=None, user=None):
        data = {}
        if modify_object is not None and user is not None:
            data['name'] = modify_object.name
            data['department_name'] = modify_object.department.name
            data['id'] = modify_object.id
        else:
            pass
        return data


    def init_from_object(self, modify_object=None, user=None):
        if modify_object is not None and user is not None:
            self.fields['name'].widget.attrs['value'] = modify_object.name
            self.fields['department_name'].widget.attrs['value'] = modify_object.department.name
            self.fields['id'].widget.attrs['value'] = modify_object.id
            return True
        else:
            return False
    
    def detail_modify(self, request):
        
        check_object = self.id_object
        if request is None:
            return None

        check_object.is_active =True
        check_object.name=self.cleaned_data['name']
        check_object.department=self.department_object
        check_object.save()
        return check_object

class CheckObjectDeleteForm(forms.Form):
    """
    检查对象删除表单
    """
    id_object = None

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def delete(self):
        if self.id_object is not None:
            self.id_object.is_active = False
            self.id_object.save()
            return True
        else:
            return False

class CheckObjectSearchForm(forms.Form):
    """
    检查对象搜索表单
    """
    is_fuzzy = False
    name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'考勤对象姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=False, 
        label=_(u'科室名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：综治办/政策法规股、政策法规股、'),
        error_messages = gl.department_name_error_messages,
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_fuzzy',
                                          }, 
                                   check_test=None,
                                   ),
        help_text=_(u' '),
        )
    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_search_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    
    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        return department_name_copy

    def data_to_session(self, request):
        request.session[gl.session_check_object_name] = self.cleaned_data['name']
        request.session[gl.session_check_object_department_name] = self.cleaned_data['department_name']
        is_fuzzy = self.cleaned_data['is_fuzzy']
        if is_fuzzy == u'is_fuzzy':
            request.session[gl.session_check_object_is_fuzzy] = is_fuzzy
        else:
            request.session[gl.session_check_object_is_fuzzy] = False
        return True
    
    def data_from_session(self, request):
        data = {}
        data['name'] = request.session.get(gl.session_check_object_name, u'')
        data['department_name'] = request.session.get(gl.session_check_object_department_name, u'')
        data['is_fuzzy'] = request.session.get(gl.session_check_object_is_fuzzy, False)
        return data

    def init_from_session(self, request):
        self.fields['name'].widget.attrs['value'] = request.session.get(gl.session_check_object_name, u'')
        self.fields['department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_department_name, u'')
        is_fuzzy = request.session.get(gl.session_check_object_is_fuzzy, False)
        if is_fuzzy == u'is_fuzzy':
            self.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
        else:
            pass
        return True
    
    def query_name(self, query_set=None):
        name = self.cleaned_data['name']
        is_fuzzy = self.is_fuzzy
        
        if query_set is None:
            return query_set

        if name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(name__startswith=name)
            else:
                query_set = query_set.filter(name__icontains=name)
                
        return query_set

    def query_department_name(self, query_set=None):
        department_name = self.cleaned_data['department_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if department_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(department__name__startswith=department_name)
            else:
                query_set = query_set.filter(department__name__icontains=department_name)

        return query_set
    
    def search(self):

        if self.cleaned_data['is_fuzzy'] == u'is_fuzzy':
            self.is_fuzzy = True
        else:
            self.is_fuzzy = False

        query_set = CheckObject.objects.filter(is_active=True)
        query_set = self.query_name(query_set)
        query_set = self.query_department_name(query_set)

        return query_set
