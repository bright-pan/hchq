#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError

from hchq.check_project.models import Check_Project
from hchq.untils import gl
import re

class CheckProjectAddForm(forms.Form):
    """
    检查项目添加表单
    """
    check_project_name_copy = None
    check_project_name = forms.CharField(
        max_length=500,
        required=True, 
        label=_(u'检查项目名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：2010年10-12月下半年环孕检'),

        )
    check_project_start_time = forms.DateField(
        max_length=10,
        required=True,
        label=_(u'开始时间')
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.check_project_time_error_messages,
        input_formats = '%Y-%m-%d'
        )
    check_project_end_time = forms.DateField(
        max_length=10,
        required=True,
        label=_(u'结束时间')
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.check_project_time_error_messages,
        input_formats = '%Y-%m-%d'
        )
    def clean_check_project_name(self):
        try:
            self.check_project_name_copy = self.data.get('check_project_name')
            self.check_project_start_time_copy = self.cleaned_data.get('check_project_start_time')
            self.check_project_start_end_copy = self.cleaned_data.get('check_project_end_time')
#            print check_project_name_copy
            if re.match(gl.check_project_name_add_re_pattern, check_project_name_copy) is None:
                raise forms.ValidationError(gl.check_project_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
        try:
            CheckProject.objects.get(name=self.check_project_name_copy)
        except ObjectDoseNotExist:
            return self.check_project_name_copy:
        raise forms.ValidationError(gl.check_project_name_error_messages['already_error'])

    def check_project_add(self, user=None):
        check_project_name_obj = None
        created = None
        if user is not None and user.is_authenticated() and self.check_project_name_copy is not None and self.check_project_start_time_copy is not None and self.check_project_end_time_copy is not None:
                check_project_name_obj, created = CheckProject.objects.get_or_create(name=self.check_project_name_copy,
                                                                                     creater=user,
                                                                                     start_time=self.check_project_start_time_copy,
                                                                                     end_time=self.check_project_end_time_copy
                                                                                     )
                if created is True:
                    pass
                else:
                    pass
        return check_project_name_obj

class CheckProjectModifyForm(forms.Form):
    """
    检查项目修改表单
    """
    check_project_name_copy = None
    check_project_id_copy = None
    check_project_object = None
    check_project_id_object = None

    check_project_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'新检查项目名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',
                                      }
                               ), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.check_project_name_error_messages,
        )
    check_project_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_project_name_error_messages,
        )
    
    def clean_check_project_name(self):
        try:
            self.check_project_name_copy = self.data.get('check_project_name')
            try:
                self.check_project_id_copy = int(self.data.get('check_project_id'))
            except ValueError:
                raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
            self.check_project_id_object = Check_Project.objects.get(pk=self.check_project_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
#            print self.check_project_name_copy
#            print type(self.check_project_id_copy)
        if re.match(gl.check_project_name_modify_re_pattern, self.check_project_name_copy) is None:
            raise forms.ValidationError(gl.check_project_name_error_messages['format_error'])
        try:
            self.check_project_object = CheckProject.objects.get(name=self.check_project_name_copy)
        except ObjectDoesNotExist:
            self.check_project_object = None
            return self.check_project_name_copy
        if self.check_project_object.id == self.check_project_id_copy:
            raise forms.ValidationError(gl.check_project_name_error_messages['already_error'])
        else:
            if self.check_project_object.is_active is True:
                raise forms.ValidationError(gl.check_project_name_error_messages['already_error'])
        return self.check_project_name_copy

    def check_project_modify(self):

        if self.check_project_object is not None:
            #如果修改对象存在
            if self.check_project_object.is_active is False:
                #如果修改后的对象是已经删除的对象则激活该对象，并将修改前的对象冻结，然后将该对象的关联也冻结。
                self.check_project_object.is_active = True
                self.check_project_object.save()
                self.check_project_id_object.is_active = False
                self.check_project_id_object.save()
                CheckProject.objects.filter(check_project=self.check_project_id_object).update(is_active=False)
                return True
            else:
                return False
        else:
            self.check_project_id_object.name = self.check_project_name_copy
            self.check_project_id_object.save()
            return True

class CheckProjectDeleteForm(forms.Form):
    """
    检查项目删除表单
    """
    check_project_id_copy = None
    check_project_id_object = None

    check_project_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_project_name_error_messages,
        )
    
    def clean_check_project_id(self):
        try:
            try:
                self.check_project_id_copy = int(self.data.get('check_project_id'))
            except ValueError:
                raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
            self.check_project_id_object = Check_Project.objects.get(pk=self.check_project_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
        return self.check_project_id_copy

    def check_project_delete(self):

        if self.check_project_id_object is not None:
            self.check_project_id_object.is_active = False
            self.check_project_id_object.save()
            Check_Project.objects.filter(check_project=self.check_project_id_object).update(is_active=False)
        else:
            return False

class CheckProjectSearchForm(forms.Form):
    """
    检查项目搜索表单
    """
    check_project_name_copy = None
    is_fuzzy_value = None
    
    check_project_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'检查项目名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',
                                      }
                               ), 
        help_text=_(u'例如：县委，政法委...'),
        error_messages = gl.check_project_name_error_messages,
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
    
    def clean_check_project_name(self):
        try:
            self.check_project_name_copy = self.data.get('check_project_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
        if re.match(gl.check_project_name_search_re_pattern, self.check_project_name_copy) is None:
            raise forms.ValidationError(gl.check_project_name_error_messages['format_error'])
#        print self.check_project_name_copy
        return self.check_project_name_copy
    
    def clean_is_fuzzy(self):
        try:
            self.is_fuzzy_value = self.data.get('is_fuzzy')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_name_error_messages['form_error'])
#        print self.is_fuzzy_value
        return self.is_fuzzy_value
    
    def fuzzy_search(self):
        if self.is_fuzzy_value == u'fuzzy_search':
            return True
        else:
            return False
        
    def is_null(self):
        if self.check_project_name_copy == u'':
            return True
        else:
            return False
    def save_to_session(self, request):
        request.session[gl.session_check_project_name] = self.check_project_name_copy
        if self.fuzzy_search():
            request.session[gl.session_check_project_is_fuzzy] = u'fuzzy_search'
        else:
            request.session[gl.session_check_project_is_fuzzy] = False
        return True
