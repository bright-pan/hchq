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
from hchq.check_object.models import *
from hchq import settings
import re
import datetime

class CheckObjectAddForm(forms.Form):
    """
    系统用户添加表单
    """

    service_area_department_object = None
    mate_service_area_department_object = None
    ctp_method_time_copy = None
    wedding_time_copy = None
    
    name = forms.CharField(
        max_length=64,
        required=True, 
        label=_(u'妻子姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三，李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    id_number = forms.CharField(
        max_length=18,
        required=True,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域'),
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委/政法委，公安局，...'),
        error_messages = gl.department_name_error_messages,
        )
    is_family = forms.CharField(
        required=True,
        label =_(u'家属'),
        help_text=_(u'例如：对象没有单位则打勾！'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_family',
                                          }, 
                                   check_test=None,
                                   ),
        )
    mate_name = forms.CharField(
        max_length=64,
        required=True,
        label=_(u'丈夫姓名'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三，李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    mate_id_number = forms.CharField(
        max_length=18,
        required=True,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    mate_service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    mate_department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委/政法委，公安局，...'),
        error_messages = gl.department_name_error_messages,
        )

    ctp_method = forms.ChoiceField(
        required=True,
        label =_(u'避孕措施'),
        choices=((u'0', u'未使用'),
                 (u'1', u'避孕环方式'),
                 (u'2', u'避孕药方式'),
                 (u'3', u'其他方式'),
                 ),
        help_text=_(u'例如：已上环则选择避孕环方式。'),
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

    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    
    def clean_id_number(self):
        try:
            id_number_copy = self.data.get('id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_add_re_pattern, id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        try:
            self.role_object = CheckObject.objects.get(id_number=id_number_copy, is_active=True)
        except ObjectDoesNotExist:
            return id_number_copy
        raise forms.ValidationError(gl.check_object_id_number_error_messages['already_error'])
        
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
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
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
    def clean_mate_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    
    def clean_mate_id_number(self):
        try:
            id_number_copy = self.data.get('id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_add_re_pattern, id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return id_number_copy

    def clean_mate_service_area_name(self):
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

    def clean_mate_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
            service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            service_area_object = ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.mate_service_area_department_object = ServiceAreaDepartment.objects.get(service_area=service_area_object, department=department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return department_name_copy
        
    def clean_ctp_method_time(self):
        try:
            self.ctp_method_time_copy = self.cleaned_data.get('ctp_method_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['form_error'])
        if self.ctp_method_time_copy is not None:
            if self.ctp_method_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['logic_error'])
        return self.ctp_method_time_copy
    def clean_wedding_time(self):
        try:
            self.wedding_time_copy = self.cleaned_data.get('wedding_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_wedding_time_error_messages['form_error'])
        if self.wedding_time_copy is not None:
            if self.wedding_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_object_wedding_time_error_messages['logic_error'])
        return self.wedding_time_copy

    
    def add(self, user = None):
        if user is not None and self.service_area_department_object is not None and self.mate_service_area_department_object is not None:
            if self.cleaned_data['is_family'] == u'is_family':
                is_family_value = True
            else:
                is_family_value = False
            try:
                file_temp = default_storage.open(u'images/photos/temp/%s.temp' % user.username)
            except IOError:
                return False
            file_path = u'images/photos/%s.jpg' % self.cleaned_data['id_number']
            default_storage.delete(file_path)
            default_storage.save(file_path, file_temp)
            file_temp.close()
            del file_temp
            try:
                check_object = CheckObject.objects.get(is_active=False, id_number=self.cleaned_data['id_number'])
            except ObjectDoesNotExist:
                CheckObject.objects.create(name=self.cleaned_data['name'],
                                           photo=file_path,
                                           id_number=self.cleaned_data['id_number'],
                                           service_area_department=self.service_area_department_object,
                                           is_family=is_family_value,
                                           mate_name=self.cleaned_data['mate_name'],
                                           mate_id_number=self.cleaned_data['mate_id_number'],
                                           mate_service_area_department=self.mate_service_area_department_object,
                                           ctp_method = self.cleaned_data['ctp_method'],
                                           ctp_method_time = self.cleaned_data['ctp_method_time'],
                                           wedding_time = self.cleaned_data['wedding_time'],
                                           creater = user,
                                           )
                return True
            check_object.is_active =True
            check_object.name=self.cleaned_data['name']
            check_object.photo=file_path
            check_object.service_area_department=self.service_area_department_object
            check_object.is_family=is_family_value
            check_object.mate_name=self.cleaned_data['mate_name']
            check_object.mate_id_number=self.cleaned_data['mate_id_number']
            check_object.mate_service_area_department=self.mate_service_area_department_object
            check_object.ctp_method = self.cleaned_data['ctp_method']
            check_object.ctp_method_time = self.cleaned_data['ctp_method_time']
            check_object.wedding_time = self.cleaned_data['wedding_time']
            check_object.creater = user
            check_object.save()
            return True
        return False
            

class CheckObjectModifyForm(forms.Form):
    """
    系统用户修改表单
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
            self.id_object = User.objects.get(pk=id_copy, is_active=True, is_superuser=False, is_staff=False)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def object(self):
        return self.id_object

class CheckObjectDetailModifyForm(forms.Form):
    """
    系统用户详细修改表单
    """

    id_object = None
    role_object = None
    service_area_department_object = None

    role_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'角色名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：技术人员，区域主管...'),
        error_messages = gl.role_name_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委/政法委，公安局，...'),
        error_messages = gl.department_name_error_messages,
        )
    is_checker = forms.CharField(
        required=True,
        label =_(u'检查人员'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_checker',
                                          }, 
                                   check_test=None,
                                   ),
        )
    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )

    def clean_role_name(self):
        try:
            role_name_copy = self.data.get('role_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
        if re.match(gl.role_name_add_re_pattern, role_name_copy) is None:
            raise forms.ValidationError(gl.role_name_error_messages['format_error'])
        try:
            self.role_object = Group.objects.get(name=role_name_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['not_exist_error'])
#        print self.role_name_copy
        return role_name_copy
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
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            service_area_object = ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.service_area_department_object = ServiceAreaDepartment.objects.get(service_area=service_area_object, department=department_object, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return department_name_copy

    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = User.objects.get(pk=id_copy, is_active=True, is_superuser=False, is_staff=False)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy


    def set_value(self, modify_object=None):
        if modify_object is not None:
            self.fields['role_name'].widget.attrs['value'] = modify_object.groups.get().name
            self.fields['service_area_name'].widget.attrs['value'] = modify_object.get_profile().service_area_department.service_area.name
            self.fields['department_name'].widget.attrs['value'] = modify_object.get_profile().service_area_department.department.name
            self.fields['id'].widget.attrs['value'] = modify_object.id
            is_checker = modify_object.get_profile().is_checker
            if is_checker is True:
                self.fields['is_checker'].widget.attrs['checked'] = u'true'
            else:
                pass
            return True
        else:
            return False

    
    def detail_modify(self):
        if self.cleaned_data['is_checker'] == u'is_checker':
            is_checker = True
        else:
            is_checker = False
        self.id_object.groups.clear()
        self.id_object.groups.add(self.role_object)
        id_object_profile = self.id_object.get_profile()
        id_object_profile.service_area_department = self.service_area_department_object
        id_object_profile.is_checker = is_checker
        id_object_profile.save()
        self.id_object.save()
        return self.id_object

class CheckObjectDeleteForm(forms.Form):
    """
    系统用户删除表单
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
            self.id_object = User.objects.get(pk=id_copy, is_active=True, is_superuser=False, is_staff=False)
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
    系统用户搜索表单
    """
    
    name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'系统用户名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三，李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    role_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'角色名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：技术人员，区域主管...'),
        error_messages = gl.role_name_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'服务区域名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=False, 
        label=_(u'单位部门名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委/政法委，公安局，...'),
        error_messages = gl.department_name_error_messages,
        )
    is_checker = forms.ChoiceField(
        required=True,
        label =_(u'检查人员'),
        choices=((u'none', u'未知'),
                 (u'true', u'是'),
                 (u'false', u'否'),
                 ),
        help_text=_(u'例如：未知代表所有人员'),
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_fuzzy',
                                          }, 
                                   check_test=None,
                                   ),
        help_text=_(u'例如：打勾代表进行模糊搜索！'),
        )
    
    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_search_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    
    def clean_role_name(self):
        try:
            role_name_copy = self.data.get('role_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
        if re.match(gl.role_name_search_re_pattern, role_name_copy) is None:
            raise forms.ValidationError(gl.role_name_error_messages['format_error'])
        return role_name_copy

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

    def data_to_session(self, request):
        request.session[gl.session_check_object_name] = self.cleaned_data['name']
        request.session[gl.session_check_object_role_name] = self.cleaned_data['role_name']
        request.session[gl.session_check_object_service_area_name] = self.cleaned_data['service_area_name']
        request.session[gl.session_check_object_department_name] = self.cleaned_data['department_name']
        request.session[gl.session_check_object_is_checker] = self.cleaned_data['is_checker']
        is_fuzzy = self.cleaned_data['is_fuzzy']
#        print is_fuzzy
        if is_fuzzy == u'is_fuzzy':
#            print u'true'
            request.session[gl.session_check_object_is_fuzzy] = is_fuzzy
        else:
#            print u'false'
            request.session[gl.session_check_object_is_fuzzy] = False
        return True
    
    def data_from_session(self, request):
        data = {}
        data['name'] = request.session.get(gl.session_check_object_name, u'')
        data['role_name'] = request.session.get(gl.session_check_object_role_name, u'')
        data['service_area_name'] = request.session.get(gl.session_check_object_service_area_name, u'')
        data['department_name'] = request.session.get(gl.session_check_object_department_name, u'')
        data['is_checker'] = request.session.get(gl.session_check_object_is_checker, u'none')
        data['is_fuzzy'] = request.session.get(gl.session_check_object_is_fuzzy, False)
#        print data['is_fuzzy']
        return data
    
    def init_from_session(self, request):
        self.fields['name'].widget.attrs['value'] = request.session.get(gl.session_check_object_name, u'')
        self.fields['role_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_role_name, u'')
        self.fields['service_area_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_service_area_name, u'')
        self.fields['department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_department_name, u'')
        self.fields['is_checker'].widget.attrs['value'] = request.session.get(gl.session_check_object_is_checker, u'none')
        is_fuzzy = request.session.get(gl.session_check_object_is_fuzzy, False)
        if is_fuzzy == u'is_fuzzy':
            self.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
        else:
            pass
        return True
    
    def search(self):
        query_set = None
        name = self.cleaned_data['name']
        service_area_name = self.cleaned_data['service_area_name']
        department_name = self.cleaned_data['department_name']
        role_name = self.cleaned_data['role_name']
        is_checker = self.cleaned_data['is_checker']
        if self.cleaned_data['is_fuzzy'] == u'is_fuzzy':
            is_fuzzy = True
        else:
            is_fuzzy = False
        
        if is_fuzzy is False:
            if is_checker == u'true':
                query_set = UserProfile.objects.filter(is_checker=True, user__is_active=True, user__is_superuser=False, user__is_staff=False)
                if role_name == u'':
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)

                    else:
                        query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)
                else:
                    query_set = query_set.filter(user__groups__name__startswith=role_name)
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__startswith=name)
                    else:
                        query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__startswith=name)
            else:
                if is_checker == u'false':
                    query_set = UserProfile.objects.filter(is_checker=False, user__is_active=True, user__is_superuser=False, user__is_staff=False)
                    if role_name == u'':
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                    else:
                        query_set = query_set.filter(user__groups__name__startswith=role_name)
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__startswith=name)
                else:
                    if is_checker == u'none':
                        query_set = UserProfile.objects.filter(user__is_active=True, user__is_superuser=False, user__is_staff=False)
                        if role_name == u'':
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                        else:
                            query_set = query_set.filter(user__groups__name__startswith=role_name)
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__startswith=name)
                    else:
                        pass
        else:
            if is_checker == u'true':
                query_set = UserProfile.objects.filter(is_checker=True, user__is_active=True, user__is_superuser=False, user__is_staff=False)
                if role_name == u'':
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)

                    else:
                        query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
                else:
                    query_set = query_set.filter(user__groups__name__icontains=role_name)
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
                    else:
                        query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__username__icontains=name)
            else:
                if is_checker == u'false':
                    query_set = UserProfile.objects.filter(is_checker=False, user__is_active=True, user__is_superuser=False, user__is_staff=False)
                    if role_name == u'':
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                    else:
                        query_set = query_set.filter(user__groups__name__icontains=role_name)
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__username__icontains=name)
                else:
                    if is_checker == u'none':
                        query_set = UserProfile.objects.filter(user__is_active=True, user__is_superuser=False, user__is_staff=False)
                        if role_name == u'':
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                        else:
                            query_set = query_set.filter(user__groups__name__icontains=role_name)
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department__name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__username__icontains=name)
                    else:
                        pass
        return query_set

