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
from hchq.account.models import UserProfile
from hchq.check_object.models import *
from hchq.check_result.models import CheckResult
from hchq.check_project.models import CheckProject
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

    pregnant = forms.ChoiceField(
        required=True,
        label =_(u'孕检'),
        choices=((u'pregnant', u'有孕'),
                 (u'unpregnant', u'无孕'),
                 ),
        help_text=_(u'例如:有孕选有孕'),
        )
    ring = forms.ChoiceField(
        required=True,
        label =_(u'环检'),
        choices=((u'ring', u'有环'),
                 (u'unring', u'无环'),
                 ),
        help_text=_(u'例如:有环选有环'),
        )
    pregnant_period = forms.IntegerField(
        required=False,
        label=_(u'怀孕周期'),
        help_text=_(u'例如：5周填5'),
        max_value=50,
        min_value=1,
        )

    checker = forms.ChoiceField(
        required=True,
        label =_(u'检查人员'),
        help_text=_(u'例如:张三'),
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
            
            choices = ()
            if user.is_superuser is False:
                service_area = user.get_profile().service_area_department.service_area
                query_set = UserProfile.objects.filter(service_area_department__service_area=service_area,
                                                       is_checker=True,
                                                       user__is_active=True,
                                                       user__is_superuser=False,
                                                       user__is_staff=False)
            else:
                query_set = UserProfile.objects.filter(is_checker=True,
                                                       user__is_active=True,
                                                       user__is_superuser=False,
                                                       user__is_staff=False)
                                
            size = query_set.count()
            for query in query_set:
                choices += (str(query.user.pk), query.user.username),
                
            self.fields['checker'].choices = choices
            self.fields['checker'].widget.attrs['size'] = size
            
            self.fields['pregnant'].choices = ((u'pregnant', u'有孕'),
                                              (u'unpregnant', u'无孕'),
                                              )
            self.fields['pregnant'].widget.attrs['size'] = u'2'
            self.fields['ring'].choices = ((u'ring', u'有环'),
                                           (u'unring', u'有孕'),
                                           )
            self.fields['ring'].widget.attrs['size'] = u'2'
            self.fields['id'].widget.attrs['value'] = check_object.id
            return True
        else:

            return False
        
    def get_check_project(self):
        try:
            check_project = CheckProject.objects.get(is_setup=True, is_active=True)
        except ObjectDoesNotExist:
            return None
        return check_project
    
    def detail_add(self, user=None):
        check_object = self.id_object
        if user is None:
            return False
        try:
            check_project = CheckProject.objects.get(is_setup=True, is_active=True)
        except ObjectDoesNotExist:
            return False
        try:
            checker_id = int(self.cleaned_data['checker'])
        except ValueError:
            return False
        try:
            checker = User.objects.get(pk=checker_id)
        except ObjectDoesNotExist:
            return False
        result = "%s %s %s" % (self.cleaned_data['pregnant'],self.cleaned_data['ring'],self.cleaned_data['pregnant_period'])

        CheckResult.objects.filter(check_object=check_object).update(is_latest=False)
        CheckResult.objects.create(check_object=check_object,
                                   check_project=check_project,
                                   checker=checker,
                                   recorder=user,
                                   result=result,)
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
            self.id_object = CheckResult.objects.get(pk=id_copy, is_active=True)
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

class CheckResultSearchForm(forms.Form):
    """
    检查结果搜索表单
    """
    is_fuzzy = False
    name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'妻子姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=False,
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
    is_family = forms.ChoiceField(
        required=True,
        label =_(u'家属'),
        help_text=_(u' '),
        choices=((u'none', u'未知'),
                 (u'true', u'是'),
                 (u'false', u'否'),
                 ),
        )

    mate_name = forms.CharField(
        max_length=64,
        required=False,
        label=_(u'丈夫姓名'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    mate_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    mate_service_area_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'服务区域'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    mate_department_name = forms.CharField(
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

    ctp_method = forms.ChoiceField(
        required=True,
        label =_(u'避孕措施'),
        choices=((u'none', u'未知'),
                 (u'method_0', u'未使用'),
                 (u'method_1', u'避孕环方式'),
                 (u'method_2', u'避孕药方式'),
                 (u'method_3', u'其他方式'),
                 ),
        help_text=_(u'例如：上环选避孕环方式'),
        )
    ctp_method_time = forms.DateField(
        required=False,
        label=_(u'实施时间'),
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.check_object_ctp_method_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    wedding_time = forms.DateField(
        required=False,
        label=_(u'结婚时间'),
        help_text=_(u'例如：1985-1-1'),
        error_messages = gl.check_object_wedding_time_error_messages,
        input_formats = ('%Y-%m-%d',)
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
    pregnant = forms.ChoiceField(
        required=True,
        label =_(u'孕检'),
        choices=((u'none', u'未知'),
                 (u'pregnant', u'有孕'),
                 (u'unpregnant', u'无孕'),
                 ),
        )
    ring = forms.ChoiceField(
        required=True,
        label =_(u'环检'),
        choices=((u'none', u'未知'),
                 (u'ring', u'有环'),
                 (u'unring', u'无环'),
                 ),
        )
    pregnant_period = forms.IntegerField(
        required=False,
        label=_(u'怀孕周期'),
        help_text=_(u'例如：5周填5'),
        max_value=50,
        min_value=1,
        )

    checker = forms.CharField(
        required=False,
        max_length=10,
        label =_(u'检查人员'),
        )
    recorder = forms.CharField(
        required=False,
        max_length=10,
        label =_(u'记录人员'),
        )
    check_project = forms.ChoiceField(
        required=True,
        label =_(u'检查项目'),
        )
    start_time = forms.DateField(
        required=False,
        label=_(u'开始时间'),
        help_text=_(u'例如：2010-10-25'),
        input_formats = ('%Y-%m-%d',)
        )
    end_time  = forms.DateField(
        required=False,
        label=_(u'结束时间'),
        help_text=_(u'例如：2010-10-25'),
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
    
    def clean_id_number(self):
        try:
            id_number_copy = self.data.get('id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return id_number_copy
    def clean_service_area_name(self):
        try:
           service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_search_re_pattern, service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        return service_area_name_copy

    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        return department_name_copy

    def clean_mate_name(self):
        try:
            mate_name_copy = self.data.get('mate_name')
            if re.match(gl.check_object_name_search_re_pattern, mate_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return mate_name_copy
    
    def clean_mate_id_number(self):
        try:
            mate_id_number_copy = self.data.get('mate_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, mate_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return mate_id_number_copy

    def clean_mate_service_area_name(self):
        try:
           mate_service_area_name_copy = self.data.get('mate_service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_search_re_pattern, mate_service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
        return mate_service_area_name_copy

    def clean_mate_department_name(self):
        try:
            mate_department_name_copy = self.data.get('mate_department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, mate_department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        return mate_department_name_copy
    
    def clean_ctp_method_time(self):
        try:
            ctp_method_time_copy = self.cleaned_data.get('ctp_method_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['form_error'])
        if ctp_method_time_copy is not None:
            if ctp_method_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['logic_error'])
        return ctp_method_time_copy
    def clean_wedding_time(self):
        try:
            wedding_time_copy = self.cleaned_data.get('wedding_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_wedding_time_error_messages['form_error'])
        if wedding_time_copy is not None:
            if wedding_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_object_wedding_time_error_messages['logic_error'])
        return wedding_time_copy
    
    def data_to_session(self, request):
        request.session[gl.session_check_object_name] = self.cleaned_data['name']
        request.session[gl.session_check_object_id_number] = self.cleaned_data['id_number']

        if request.user.has_perm('department.unlocal'):
            request.session[gl.session_check_object_service_area_name] = self.cleaned_data['service_area_name']
        else:
            request.session[gl.session_check_object_service_area_name] = request.user.get_profile().service_area_department.service_area.name
        
        request.session[gl.session_check_object_department_name] = self.cleaned_data['department_name']
        request.session[gl.session_check_object_is_family] = self.cleaned_data['is_family']
        request.session[gl.session_check_object_mate_name] = self.cleaned_data['mate_name']
        request.session[gl.session_check_object_mate_id_number] = self.cleaned_data['mate_id_number']
        request.session[gl.session_check_object_mate_service_area_name] = self.cleaned_data['mate_service_area_name']
        request.session[gl.session_check_object_mate_department_name] = self.cleaned_data['mate_department_name']
        request.session[gl.session_check_object_ctp_method] = self.cleaned_data['ctp_method']

        if self.cleaned_data['ctp_method_time'] is not None:
            request.session[gl.session_check_object_ctp_method_time] = self.cleaned_data['ctp_method_time'].isoformat()
        else:
            request.session[gl.session_check_object_ctp_method_time] = u''
        if self.cleaned_data['wedding_time'] is not None:
            request.session[gl.session_check_object_wedding_time] = self.cleaned_data['wedding_time'].isoformat()
        else:
            request.session[gl.session_check_object_wedding_time] = u''
        is_fuzzy = self.cleaned_data['is_fuzzy']
#        print is_fuzzy
        if is_fuzzy == u'is_fuzzy':
#            print u'true'
            request.session[gl.session_check_object_is_fuzzy] = is_fuzzy
        else:
#            print u'false'
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

        request.session[gl.session_check_result_pregnant] = self.cleaned_data['pregnant']
        request.session[gl.session_check_result_ring] = self.cleaned_data['ring']
        request.session[gl.session_check_result_pregnant_period] = self.data['pregnant_period']
        request.session[gl.session_check_result_checker] = self.cleaned_data['checker']
        request.session[gl.session_check_result_recorder] = self.cleaned_data['recorder']
        request.session[gl.session_check_result_check_project] = self.cleaned_data['check_project']
        
        return True
    
    def data_from_session(self, request):
        data = {}
        data['name'] = request.session.get(gl.session_check_object_name, u'')
        data['id_number'] = request.session.get(gl.session_check_object_id_number, u'')
        if request.user.has_perm('department.unlocal'):
            data['service_area_name'] = request.session.get(gl.session_check_object_service_area_name, u'')
        else:
            data['service_area_name'] = request.user.get_profile().service_area_department.service_area.name
        data['department_name'] = request.session.get(gl.session_check_object_department_name, u'')
        data['is_family'] = request.session.get(gl.session_check_object_is_family, u'none')
        data['mate_name'] = request.session.get(gl.session_check_object_mate_name, u'')
        data['mate_id_number'] = request.session.get(gl.session_check_object_mate_id_number, u'')
        data['mate_service_area_name'] = request.session.get(gl.session_check_object_mate_service_area_name, u'')
        data['mate_department_name'] = request.session.get(gl.session_check_object_mate_department_name, u'')
        data['ctp_method'] = request.session.get(gl.session_check_object_ctp_method, u'none')
        data['ctp_method_time'] = request.session.get(gl.session_check_object_ctp_method_time, u'')
        data['wedding_time'] = request.session.get(gl.session_check_object_wedding_time, u'')
        data['is_fuzzy'] = request.session.get(gl.session_check_object_is_fuzzy, False)
        #结果
        data['pregnant'] = request.session.get(gl.session_check_result_pregnant, u'none')
        data['ring'] = request.session.get(gl.session_check_result_ring, u'none')
        data['pregnant_period'] = request.session.get(gl.session_check_result_pregnant_period, u'')
        data['checker'] = request.session.get(gl.session_check_result_checker, u'')
        data['recorder'] = request.session.get(gl.session_check_result_recorder, u'')
        data['check_project'] = request.session.get(gl.session_check_result_check_project, u'none')
        data['start_time'] = request.session.get(gl.session_check_result_start_time, u'')
        data['end_time'] = request.session.get(gl.session_check_result_end_time, u'')
#        print data['is_fuzzy']
        return data
    
    def init_from_session(self, request):
        self.fields['name'].widget.attrs['value'] = request.session.get(gl.session_check_object_name, u'')
        self.fields['id_number'].widget.attrs['value'] = request.session.get(gl.session_check_object_id_number, u'')
        if request.user.has_perm('department.unlocal'):
            self.fields['service_area_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_service_area_name, u'')
        else:
            self.fields['service_area_name'].widget.attrs['value'] = request.user.get_profile().service_area_department.service_area.name
            self.fields['service_area_name'].widget.attrs['readonly'] = True
        self.fields['department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_department_name, u'')
        self.fields['is_family'].widget.attrs['value'] = request.session.get(gl.session_check_object_is_family, u'none')
        self.fields['mate_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_name, u'')
        self.fields['mate_id_number'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_id_number, u'')
        self.fields['mate_service_area_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_service_area_name, u'')
        self.fields['mate_department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_department_name, u'')
        self.fields['ctp_method'].widget.attrs['value'] = request.session.get(gl.session_check_object_ctp_method, u'none')
        self.fields['ctp_method_time'].widget.attrs['value'] = request.session.get(gl.session_check_object_ctp_method_time, u'')
        self.fields['wedding_time'].widget.attrs['value'] = request.session.get(gl.session_check_object_wedding_time, u'')
        is_fuzzy = request.session.get(gl.session_check_object_is_fuzzy, False)
        if is_fuzzy == u'is_fuzzy':
            self.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
        else:
            pass
        
        self.fields['pregnant'].widget.attrs['value'] = request.session.get(gl.session_check_result_pregnant, u'none')
        self.fields['ring'].widget.attrs['value'] = request.session.get(gl.session_check_result_ring, u'none')
        self.fields['pregnant_period'].widget.attrs['value'] = request.session.get(gl.session_check_result_pregnant_period, u'')
        self.fields['checker'].widget.attrs['value'] = request.session.get(gl.session_check_result_checker, u'')
        self.fields['recorder'].widget.attrs['value'] = request.session.get(gl.session_check_result_recorder, u'')
        self.fields['check_project'].widget.attrs['value'] = request.session.get(gl.session_check_result_check_project, u'none')
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

    def query_id_number(self, query_set=None):
        id_number = self.cleaned_data['id_number']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if id_number == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(check_object__id_number__startswith=id_number)
            else:
                query_set = query_set.filter(check_object__id_number__icontains=id_number)

        return query_set
    
    def query_service_area_name(self, query_set=None):
        service_area_name = self.cleaned_data['service_area_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if service_area_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(check_object__service_area_department__service_area__name__startswith=service_area_name)
            else:
                query_set = query_set.filter(check_object__service_area_department__service_area__name__icontains=service_area_name)

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
                query_set = query_set.filter(check_object__service_area_department__department__name__startswith=department_name)
            else:
                query_set = query_set.filter(check_object__service_area_department__department__name__icontains=department_name)

        return query_set

    def query_is_family(self, query_set=None):
        is_family = self.cleaned_data['is_family']

        if query_set is None:
            return query_set
        
        if is_family == u'true':
            query_set = query_set.filter(check_object__is_family=True)
        else:
            if is_family == u'false':
                query_set = query_set.filter(check_object__is_family=False)
            else:
                if is_family == u'none':
                    pass
                else:
                    pass

        return query_set

    def query_mate_name(self, query_set=None):
        mate_name = self.cleaned_data['mate_name']
        is_fuzzy = self.is_fuzzy
        
        if query_set is None:
            return query_set

        if mate_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(check_object__mate_name__startswith=mate_name)
            else:
                query_set = query_set.filter(check_object__mate_name__icontains=mate_name)
                
        return query_set

    def query_mate_id_number(self, query_set=None):
        mate_id_number = self.cleaned_data['mate_id_number']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if mate_id_number == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(check_object__mate_id_number__startswith=mate_id_number)
            else:
                query_set = query_set.filter(check_object__mate_id_number__icontains=mate_id_number)

        return query_set
    
    def query_mate_service_area_name(self, query_set=None):
        mate_service_area_name = self.cleaned_data['mate_service_area_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if mate_service_area_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(check_object__mate_service_area_department__service_area__name__startswith=mate_service_area_name)
            else:
                query_set = query_set.filter(check_object__mate_service_area_department__service_area__name__icontains=mate_service_area_name)

        return query_set
    
    def query_mate_department_name(self, query_set=None):
        mate_department_name = self.cleaned_data['mate_department_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if mate_department_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(check_object__mate_service_area_department__department__name__startswith=mate_department_name)
            else:
                query_set = query_set.filter(check_object__mate_service_area_department__department__name__icontains=mate_department_name)

        return query_set

    def query_ctp_method(self, query_set=None):
        ctp_method = self.cleaned_data['ctp_method']

        if query_set is None:
            return query_set
        
        if ctp_method == u'none':
            pass
        else:
            query_set = query_set.filter(check_object__ctp_method=ctp_method)
            
        return query_set
    
    def query_ctp_method_time(self, query_set=None):
        ctp_method_time = self.cleaned_data['ctp_method_time']

        if query_set is None:
            return query_set

        if ctp_method_time == None:
            pass
        else:
            query_set = query_set.filter(check_object__ctp_method_time=ctp_method_time)
            
        return query_set
    
    def query_wedding_time(self, query_set=None):
        wedding_time = self.cleaned_data['wedding_time']

        if query_set is None:
            return query_set

        if wedding_time == None:
            pass
        else:
            query_set = query_set.filter(check_object__wedding_time=wedding_time)
        
        return query_set

    def query_pregnant(self, query_set=None):
        pregnant = self.cleaned_data['pregnant']

        if query_set is None:
            return query_set

        if pregnant == u'none':
            pass
        else:
            query_set = query_set.filter(result__icontains=pregnant)

        return query_set
    def query_ring(self, query_set=None):
        ring = self.cleaned_data['ring']

        if query_set is None:
            return query_set

        if ring == u'none':
            pass
        else:
            query_set = query_set.filter(result__icontains=ring)

        return query_set
    
    def query_pregnant_period(self, query_set=None):
        pregnant_period = self.cleaned_data['pregnant_period']

        if query_set is None:
            return query_set

        if pregnant_period is None:
            pass
        else:
            query_set = query_set.filter(result__icontains=pregnant_period)

        return query_set

    def query_check_project(self, query_set=None):
        try:
            check_project_id = int(self.cleaned_data['check_project'])
        except ValueError:
            return query_set
        try:
            check_project = CheckProject.objects.get(pk=check_project_id)
        except ObjectDoesNotExist:
            return query_set
        
        if query_set is None:
            return query_set

        query_set = query_set.filter(check_project=check_project)

        return query_set

    def query_checker(self, query_set=None):
        checker = self.cleaned_data['checker']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if checker == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(checker__username__startswith=checker)
            else:
                query_set = query_set.filter(checker__username__icontains=checker)

        return query_set

    def query_recorder(self, query_set=None):
        recorder = self.cleaned_data['recorder']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if recorder == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(recorder__username__startswith=recorder)
            else:
                query_set = query_set.filter(recorder__username__icontains=recorder)

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

    def init_check_project(self):
        choices = ((u'none',u'未知'),)
        query_set = CheckProject.objects.filter(is_active=True) 
        for query in query_set:
            choices += (str(query.pk), query.name),
        self.fields['check_project'].choices = choices

    def search(self):

        if self.cleaned_data['is_fuzzy'] == u'is_fuzzy':
            self.is_fuzzy = True
        else:
            self.is_fuzzy = False

        query_set = CheckResult.objects.filter(is_latest=True)

        query_set = self.query_pregnant(query_set)
        query_set = self.query_ring(query_set)
        query_set = self.query_pregnant_period(query_set)
        query_set = self.query_check_project(query_set)
        query_set = self.query_checker(query_set)
        query_set = self.query_recorder(query_set)
        query_set = self.query_start_time(query_set)
        query_set = self.query_end_time(query_set)

        query_set = query_set.filter(check_object__is_active=True)
        
        query_set = self.query_name(query_set)
        query_set = self.query_id_number(query_set)
        query_set = self.query_mate_name(query_set)
        query_set = self.query_mate_id_number(query_set)
        query_set = self.query_service_area_name(query_set)
        query_set = self.query_department_name(query_set)
        query_set = self.query_mate_service_area_name(query_set)
        query_set = self.query_mate_department_name(query_set)
        query_set = self.query_ctp_method(query_set)
        query_set = self.query_is_family(query_set)
        query_set = self.query_ctp_method_time(query_set)
        query_set = self.query_wedding_time(query_set)
        
        
        
        return query_set
