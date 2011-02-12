#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from hchq.untils import gl
from hchq.account.models import UserProfile
from hchq.check_object.models import *
from hchq.check_result.models import CheckResult
from hchq import settings
import re
import datetime

class CheckResultAddForm(forms.Form):
    """
    检查结果修改表单
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
    
    def object(self):
        return self.id_object

class CheckResultDetailAddForm(forms.Form):
    """
    检查结果详细修改表单
    """
    id_object = None
    
    days = forms.DecimalField(
        required=True, 
        label=_(u'请假天数'),
        help_text=_(u'例如:半天：0.5，一天半：1.5。'),
        max_digits=9,
        decimal_places=1,
        )
    desc = forms.CharField(
        max_length=200,
        required=False, 
        label=_(u'请假原因描述'), 
        widget=forms.Textarea(attrs={'class':'',
                                     'size':'30',
                                     'rows':'5',
                                     }
                              ), 
        error_messages = gl.department_name_error_messages,
        )

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
    def init_value(self, user=None, check_object=None):
        if user is not None and check_object is not None:
            self.fields['id'].widget.attrs['value'] = check_object.id
            print '***********8'
            return True
        else:

            return False
    
    def detail_add(self, user=None):
        check_object = self.id_object
        if user is None:
            return False
        CheckResult.objects.create(check_object=check_object,
                                   days = self.cleaned_data['days'],
                                   desc = self.cleaned_data['desc'],
                                   recorder=user,)
        return True
    
class CheckResultDeleteForm(forms.Form):
    """
    检查结果删除表单
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
            self.id_object = CheckResult.objects.get(pk=id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def delete(self):
        if self.id_object is not None:
            self.id_object.delete()
            return True
        else:
            return False

class CheckResultSearchForm(forms.Form):
    """
    检查结果搜索表单
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
    start_time = forms.DateField(
        required=False,
        label=_(u'开始时间'),
        help_text=_(u'例如：2010-10-1'),
        input_formats = ('%Y-%m-%d',)
        )
    end_time  = forms.DateField(
        required=False,
        label=_(u'结束时间'),
        help_text=_(u'例如：2010-10-31'),
        input_formats = ('%Y-%m-%d',)
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
            
        #结果查询
        if self.cleaned_data['start_time'] is not None:
            request.session[gl.session_check_result_start_time] = self.cleaned_data['start_time'].isoformat()
        else:
            request.session[gl.session_check_result_start_time] = u''
        if self.cleaned_data['end_time'] is not None:
            request.session[gl.session_check_result_end_time] = self.cleaned_data['end_time'].isoformat()
        else:
            request.session[gl.session_check_result_end_time] = u''

        return True
    
    def data_from_session(self, request):
        data = {}
        data['name'] = request.session.get(gl.session_check_object_name, u'')
        data['department_name'] = request.session.get(gl.session_check_object_department_name, u'')
        data['is_fuzzy'] = request.session.get(gl.session_check_object_is_fuzzy, False)
        #结果
        data['start_time'] = request.session.get(gl.session_check_result_start_time, u'')
        data['end_time'] = request.session.get(gl.session_check_result_end_time, u'')
        return data
    
    def init_from_session(self, request):
        self.fields['name'].widget.attrs['value'] = request.session.get(gl.session_check_object_name, u'')
        self.fields['department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_department_name, u'')
        is_fuzzy = request.session.get(gl.session_check_object_is_fuzzy, False)
        if is_fuzzy == u'is_fuzzy':
            self.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
        else:
            pass
        
        self.fields['start_time'].widget.attrs['value'] = request.session.get(gl.session_check_result_start_time, u'')
        self.fields['end_time'].widget.attrs['value'] = request.session.get(gl.session_check_result_end_time, u'')

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
                query_set = query_set.filter(check_object__name__startswith=name)
            else:
                query_set = query_set.filter(check_object__name__icontains=name)
                
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
                query_set = query_set.filter(check_object__department__name__startswith=department_name)
            else:
                query_set = query_set.filter(check_object__department__name__icontains=department_name)

        return query_set

    def query_start_time(self, query_set=None):
        start_time = self.cleaned_data['start_time']

        if query_set is None:
            return query_set

        if start_time == None:
            pass
        else:
            start_time = datetime.datetime(start_time.year, start_time.month, start_time.day)
            query_set = query_set.filter(check_time__gte=start_time)
        
        return query_set
    def query_end_time(self, query_set=None):
        end_time = self.cleaned_data['end_time']
        if query_set is None:
            return query_set

        if end_time == None:
            pass
        else:
            end_time = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59, 59)
            query_set = query_set.filter(check_time__lte=end_time)
        return query_set

    def search(self):

        if self.cleaned_data['is_fuzzy'] == u'is_fuzzy':
            self.is_fuzzy = True
        else:
            self.is_fuzzy = False

        query_set = CheckResult.objects.all()

        query_set = self.query_name(query_set)
        query_set = self.query_department_name(query_set)
        query_set = self.query_start_time(query_set)
        query_set = self.query_end_time(query_set)

        return query_set

