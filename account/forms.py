#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist

from hchq.untils import gl
from hchq.service_area.models import ServiceArea, ServiceAreaDepartment
from hchq.department.models import Department
from hchq.account.models import UserProfile
from hchq import settings
import re


class LoginForm(forms.Form):
    """
    用户登入表单
    """
    user = None
    
    username = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'用户名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：张三, 张三A, 张三1'),
        error_messages = gl.account_name_error_messages,
        )
    password = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'用户密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                          'size':'30',}), 
        help_text=_(u'例如：123456, pa123456'),
        error_messages = gl.account_password_error_messages,
        )
    
    def clean_username(self):
        try:
            username = self.data.get('username')
            if re.match(gl.account_name_re_pattern, username) is None:
                raise forms.ValidationError(gl.account_name_error_messages['format_error'])
            User.objects.get(username=username, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['do_not_exist'])
        return username

    def clean_password(self):

        try:
            username = self.data.get('username')
            password = self.data.get('password')
            if re.match(gl.account_password_re_pattern, password ) is None:
                raise forms.ValidationError(gl.account_password_error_messages['format_error'])
            from django.contrib.auth import authenticate
            self.user = authenticate(username = username, password = password)
            if self.user is None:
                raise forms.ValidationError(gl.account_password_error_messages['password_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['do_not_exist'])
        return password
    
    def get_user(self):
        return self.user
    
    def get_user_id(self):
        if self.user is None:
            return None
        else:
            return self.user.id

class ModifyPasswordForm(forms.Form):
    """
    修改密码表单
    """
    password_new = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'新密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                          'size':'30',}), 
        help_text=_(u'例如：123456, pa123456'),
        error_messages = gl.account_password_error_messages,
        )
    password_confirm = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'确认新密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                          'size':'30',}), 
        help_text=_(u'请重新输入密码，例如：123456, pa123456'),
        error_messages = gl.account_password_error_messages,
        )
    
    def clean_password_new(self):
        try:
            password_new_copy = self.data.get('password_new')
            password_confirm_copy = self.data.get('password_confirm')        
            if re.match(gl.account_password_re_pattern, password_new_copy ) is None:
                raise forms.ValidationError(gl.account_password_error_messages['format_error'])
            if password_new_copy != password_confirm_copy:
                raise forms.ValidationError(gl.account_password_error_messages['password_confirm_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_password_error_messages['password_form_error'])
        return password_new_copy

    def clean_password_confirm(self):
        try:
            password_new_copy = self.data.get('password_new')
            password_confirm_copy = self.data.get('password_confirm')        
            if re.match(gl.account_password_re_pattern, password_confirm_copy ) is None:
                raise forms.ValidationError(gl.account_password_error_messages['format_error'])
            if password_new_copy != password_confirm_copy:
                raise forms.ValidationError(gl.account_password_error_messages['password_confirm_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_password_error_messages['form_error'])
        return password_confirm_copy

    def password_save(self, user=None):
        """
        修改用户密码并保存。
        """
        if user is not None and user.is_authenticated():
            user.set_password(self.cleaned_data.get('password_confirm'))
            user.save()
            return True
        return False

class RoleSearchForm(forms.Form):
    """
    角色搜索表单
    """
    role_name_copy = None
    is_fuzzy_value = None
    
    role_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'角色名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：技术人员，区域主任'),
        error_messages = gl.role_name_error_messages,
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'fuzzy_search',}, check_test=None),
        )
    
    def clean_role_name(self):
        try:
            self.role_name_copy = self.data.get('role_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
        if re.match(gl.role_name_search_re_pattern, self.role_name_copy) is None:
            raise forms.ValidationError(gl.role_name_error_messages['format_error'])
#        print self.role_name_copy
        return self.role_name_copy
    
    def clean_is_fuzzy(self):
        try:
            self.is_fuzzy_value = self.data.get('is_fuzzy')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
#        print self.is_fuzzy_value
        return self.is_fuzzy_value
    
    def fuzzy_search(self):
        if self.is_fuzzy_value == u'fuzzy_search':
            return True
        else:
            return False
        
    def is_null(self):
        if self.role_name_copy == u'':
            return True
        else:
            return False
    def save_to_session(self, request):
        request.session[gl.session_role_name] = self.role_name_copy
        if self.fuzzy_search():
            request.session[gl.session_role_is_fuzzy] = u'fuzzy_search'
        else:
            request.session[gl.session_role_is_fuzzy] = False
        return True
    
class RoleAddForm(forms.Form):
    """
    角色添加表单
    """
    role_name_set = None
    role_name = forms.CharField(
        max_length=500,
        required=True, 
        label=_(u'角色名称'), 
        widget=forms.Textarea(attrs={'class':'',
                                     'size':'30',
                                     'rows':'3',
                                     }
                              ), 
        help_text=_(u'例如：技术人员，区域主任/检查人员...'),
        error_messages = gl.role_name_error_messages,
        )
    
    def clean_role_name(self):
        try:
            role_name_copy = self.data.get('role_name')
#            print role_name_copy
            if re.match(gl.role_name_add_re_pattern, role_name_copy) is None:
                raise forms.ValidationError(gl.role_name_error_messages['format_error'])
            self.role_name_set = set(filter(gl.filter_null_string, role_name_copy.split(u'/')))
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
        return self.role_name_set

    def role_add(self):
        role_name_list = []
        role_name_obj = None
        created = None
        if self.role_name_set is not None:
            for role_name_copy in self.role_name_set:
                role_name_obj, created = Group.objects.get_or_create(name=role_name_copy)
                if created is True:
                    role_name_list.append(role_name_obj)
                else:
                    pass
        return role_name_list

class RoleDeleteForm(forms.Form):
    """
    角色删除表单
    """
    role_id_copy = None
    role_id_object = None

    role_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.role_name_error_messages,
        )
    
    def clean_role_id(self):
        try:
            try:
                self.role_id_copy = int(self.data.get('role_id'))
            except ValueError:
                raise forms.ValidationError(gl.role_name_error_messages['form_error'])
            self.role_id_object = Group.objects.get(pk=self.role_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
        return self.role_id_copy

    def role_delete(self):

        if self.role_id_object is not None:
            self.role_id_object.delete()
            return True
        else:
            return False
    

class RoleModifyForm(forms.Form):
    """
    角色修改表单
    """
    role_name_copy = None
    role_id_copy = None
    role_object = None
    role_id_object = None

    role_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'新角色名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：技术人员，区域主管...'),
        error_messages = gl.role_name_error_messages,
        )
    role_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.role_name_error_messages,
        )
    
    def clean_role_name(self):
        try:
            self.role_name_copy = self.data.get('role_name')
            try:
                self.role_id_copy = int(self.data.get('role_id'))
            except ValueError:
                raise forms.ValidationError(gl.role_name_error_messages['form_error'])
            self.role_id_object = Group.objects.get(pk=self.role_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.role_name_error_messages['form_error'])
#            print self.role_name_copy
#            print type(self.role_id_copy)
        if re.match(gl.role_name_modify_re_pattern, self.role_name_copy) is None:
            raise forms.ValidationError(gl.role_name_error_messages['format_error'])
        try:
            self.role_object = Group.objects.get(name=self.role_name_copy)
        except ObjectDoesNotExist:
            self.role_object = None
            return self.role_name_copy
        if self.role_object.id == self.role_id_copy:
            raise forms.ValidationError(gl.role_name_error_messages['already_error'])
        return self.role_name_copy

    def role_modify(self):

        if self.role_object is not None:
            #如果修改对象存在
            pass
        else:
            self.role_id_object.name = self.role_name_copy
            self.role_id_object.save()
            return True

class RolePermissionAddForm(forms.Form):
    """
    权限添加表单
    """
    role_permission_name_set = None
    role_permission_name = forms.MultipleChoiceField(
        required=True,
        label=_(u'权限名称'), 
        widget=forms.SelectMultiple( attrs={'class':'',
                                           'size':'30',},
                                    ), 
        help_text=_(u'帮助：按住键盘Ctrl键为多选！'),
        error_messages = gl.permission_name_error_messages,
        )

    def role_permission_add(self, role=None):
        role_permission_name_copy = self.cleaned_data.get('role_permission_name')
#        print type(role_permission_name_copy)
        role_permission_name_obj = None
        created = None
        if role is not None:
            for item in role_permission_name_copy:
                try:
                    permission_id = int(item)
                except ValueError:
                    return False
                try:
                    permission = Permission.objects.get(pk=permission_id)
                except ObjectDoesNotExist:
                    return False
                try:
                    role.permissions.get(pk=permission.id)
                except ObjectDoesNotExist:
                    role.permissions.add(permission)
            role.save()
        return True

    
class RolePermissionSearchForm(forms.Form):
    """
    权限搜索表单
    """
    role_permission_name_copy = None
    is_fuzzy_value = None
    
    role_permission_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'权限名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',
                                      }
                               ), 
        help_text=_(u'例如：添加用户，添加检查人员...'),
        error_messages = gl.permission_name_error_messages,
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
    
    def clean_role_permission_name(self):
        try:
            self.role_permission_name_copy = self.data.get('role_permission_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.permission_name_error_messages['form_error'])
        if re.match(gl.permission_name_search_re_pattern, self.role_permission_name_copy) is None:
            raise forms.ValidationError(gl.permission_name_error_messages['format_error'])
#        print self.role_permission_name_copy
        return self.role_permission_name_copy
    
    def clean_is_fuzzy(self):
        try:
            self.is_fuzzy_value = self.data.get('is_fuzzy')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.permission_name_error_messages['form_error'])
#        print self.is_fuzzy_value
        return self.is_fuzzy_value
    
    def fuzzy_search(self):
        if self.is_fuzzy_value == u'fuzzy_search':
            return True
        else:
            return False
        
    def is_null(self):
        if self.role_permission_name_copy == u'':
            return True
        else:
            return False
    def save_to_session(self, request):
        request.session[gl.session_role_permission_name] = self.role_permission_name_copy
        if self.fuzzy_search():
            request.session[gl.session_role_permission_is_fuzzy] = u'fuzzy_search'
        else:
            request.session[gl.session_role_permission_is_fuzzy] = False
        return True

class RolePermissionDeleteForm(forms.Form):
    """
    权限删除表单
    """
    role_permission_id_copy = None

    role_permission_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.permission_name_error_messages,
        )
    
    def clean_role_permission_id(self):
        try:
            try:
                self.role_permission_id_copy = int(self.data.get('role_permission_id'))
            except ValueError:
                raise forms.ValidationError(gl.permission_name_error_messages['form_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.permission_name_error_messages['form_error'])
        return self.role_permission_id_copy

    def role_permission_delete(self, role=None):

        if role is not None and self.role_permission_id_copy is not None:
            try:
                role_permission_id_object = role.permissions.get(pk = self.role_permission_id_copy)
            except ObjectDoesNotExist:
                return False
            role.permissions.remove(pole_permission_id_object)
            role.save()
            return True
        return False


class AccountAddForm(forms.Form):
    """
    系统用户添加表单
    """
    role_object = None
    service_area_department_object = None
    
    name = forms.CharField(
        max_length=64,
        required=True, 
        label=_(u'系统用户名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三，李四'),
        error_messages = gl.account_name_error_messages,
        )
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

    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.account_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.account_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
        try:
            User.objects.get(is_active=True, username=name_copy)
        except ObjectDoesNotExist:
            return name_copy
        raise forms.ValidationError(gl.account_name_error_messages['already_error'])
    
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
            ServiceArea.objects.get(name=service_area_name_copy)
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
            department_object = Department.objects.get(name=department_name_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            service_area_object = ServiceArea.objects.get(name=service_area_name_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.service_area_department_object = ServiceAreaDepartment.objects.get(service_area=service_area_object, department=department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return department_name_copy

    
    def add(self):
        user_object = None
        if self.service_area_department_object is not None:
            if self.cleaned_data['is_checker'] == u'is_checker':
                is_checker_bool_value = True
            else:
                is_checker_bool_value = False
            try:
                user_object = User.objects.get(is_active=False, username=self.cleaned_data['name'])
            except ObjectDoesNotExist:
                user_object = User.objects.create_user(username=self.cleaned_data['name'],
                                                    email=settings.ACCOUNT_DEFAULT_EMAIL,
                                                    password=settings.ACCOUNT_DEFAULT_PASSWORD
                                                    )
                UserProfile.objects.create(user=user_object,
                                           is_checker=is_checker_bool_value,
                                           service_area_department=self.service_area_department_object,
                                           )
                return user_object
            user_object.is_active = True
            user_object_profile = user_object.get_profile()
            user_object_profile.is_checker = is_checker_bool_value
            user_object_profile.service_area_department=self.service_area_department_object
            user_object_profile.save()
            user_object.save()
            return user_object
        return user_object
            

class AccountModifyForm(forms.Form):
    """
    系统用户修改表单
    """

    id_copy = None
    id_object = None


    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.account_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                self.id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.account_name_error_messages['form_error'])
            self.id_object = Account.objects.get(is_active=True, pk=self.id_copy)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
        return self.id_copy

    def object(self):
        return self.id_object


class AccountDetailModifyForm(forms.Form):
    """
    系统用户详细修改表单
    """
    start_time_copy = None
    end_time_copy = None
    
    id_copy = None
    id_object = None

    start_time = forms.DateField(
        required=True,
        label=_(u'开始时间'),
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.account_name_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    end_time = forms.DateField(
        required=True,
        label=_(u'结束时间'),
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.account_name_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.account_name_error_messages,
        )


    def clean_start_time(self):
        try:
            self.start_time_copy = self.cleaned_data.get('start_time')
            self.end_time_copy = self.cleaned_data.get('end_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
        if self.start_time_copy is not None  and self.end_time_copy is not None:
            if self.start_time_copy > self.end_time_copy:
                raise forms.ValidationError(gl.account_name_error_messages['logic_error'])
        return self.start_time_copy

    def clean_end_time(self):
        try:
            self.start_time_copy = self.cleaned_data.get('start_time')
            self.end_time_copy = self.cleaned_data.get('end_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
        if self.start_time_copy is not None  and self.end_time_copy is not None:
            if self.start_time_copy > self.end_time_copy:
                raise forms.ValidationError(gl.account_name_error_messages['logic_error'])
        return self.end_time_copy
    def clean_id(self):
        try:
            try:
                self.id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.account_name_error_messages['form_error'])
            self.id_object = Account.objects.get(is_active=True, pk=self.id_copy)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
        return self.id_copy


    def set_value(self, modify_object=None):
        self.fields['start_time'].widget.attrs['value'] = modify_object.start_time.isoformat()
        self.fields['end_time'].widget.attrs['value'] = modify_object.end_time.isoformat()
        self.fields['id'].widget.attrs['value'] = modify_object.id
        return modify_object
    
    def detail_modify(self):
        
        self.id_object.start_time = self.start_time_copy
        self.id_object.end_time = self.end_time_copy
        self.id_object.save()
        return self.id_object

class AccountDeleteForm(forms.Form):
    """
    系统用户删除表单
    """
    id_copy = None
    id_object = None

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.account_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                self.id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.account_name_error_messages['form_error'])
            self.id_object = Account.objects.get(pk=self.id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
        return self.id_copy

    def delete(self):

        if self.id_object is not None:
            self.id_object.is_active = False
            self.id_object.save()
        else:
            return False

class AccountSearchForm(forms.Form):
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
        error_messages = gl.account_name_error_messages,
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
                 )
        )
    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_fuzzy',
                                          }, 
                                   check_test=None,
                                   ),
        )
    
    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl._name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.account_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.account_name_error_messages['form_error'])
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

    def save_to_session(self, request):
        request.session[gl.session_account_name] = self.cleaned_data['name']
        request.session[gl.session_account_role_name] = self.cleaned_data['role_name']
        request.session[gl.session_account_service_area_name] = self.cleaned_data['service_area_name']
        request.session[gl.session_account_department_name] = self.cleaned_data['department_name']
        request.session[gl.session_account_is_checker] = self.cleaned_data['is_checker']
        request.session[gl.session_account_is_fuzzy] = self.cleaned_data['is_fuzzy']
        return True

    def read_from_session(self, request):
        self.fields['name'].widget.attrs['value'] = request.session[gl.session_account_name]
        self.fields['role_name'].widget.attrs['value'] = request.session[gl.session_account_role_name]
        self.fields['service_area_name'].widget.attrs['value'] = request.session[gl.session_account_service_area_name]
        self.fields['department_name'].widget.attrs['value'] = request.session[gl.session_account_department_name]
        self.fields['is_checker'].widget.attrs['value'] = request.session[gl.session_account_is_checker]
        self.fields['is_fuzzy'].widget.attrs['value'] = request.session[gl.session_account_is_fuzzy]
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
                query_set = UserProfile.objects.filter(is_checker=True)
                if role_name == u'':
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
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
                                query_set = query_set.filter(user__name__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__startswith=name)
                else:
                    query_set = query_set.filter(user__groups__name__startswith=role_name)
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
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
                                query_set = query_set.filter(user__name__startswith=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__startswith=name)
            else:
                if is_checker == u'false':
                    query_set = UserProfile.objects.filter(is_checker=False)
                    if role_name == u'':
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
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
                                    query_set = query_set.filter(user__name__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__startswith=name)
                    else:
                        query_set = query_set.filter(user__groups__name__startswith=role_name)
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
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
                                    query_set = query_set.filter(user__name__startswith=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__startswith=name)
                else:
                    if is_checker == u'none':
                        query_set = UserProfile.objects.all()
                        if role_name == u'':
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
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
                                        query_set = query_set.filter(user__name__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__startswith=name)
                        else:
                            query_set = query_set.filter(user__groups__name__startswith=role_name)
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
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
                                        query_set = query_set.filter(user__name__startswith=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__startswith=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__startswith=name)
                    else:
                        pass
        else:
            if is_checker == u'true':
                query_set = UserProfile.objects.filter(is_checker=True)
                if role_name == u'':
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)

                    else:
                        query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
                else:
                    query_set = query_set.filter(user__groups__name__icontains=role_name)
                    if service_area_name == u'':
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
                    else:
                        query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                        if department_name == u'':
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                            if name == u'':
                                pass
                            else:
                                query_set = query_set.filter(user__name__icontains=name)
            else:
                if is_checker == u'false':
                    query_set = UserProfile.objects.filter(is_checker=False)
                    if role_name == u'':
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                    else:
                        query_set = query_set.filter(user__groups__name__icontains=role_name)
                        if service_area_name == u'':
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                            if department_name == u'':
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                if name == u'':
                                    pass
                                else:
                                    query_set = query_set.filter(user__name__icontains=name)
                else:
                    if is_checker == u'none':
                        query_set = UserProfile.objects.all()
                        if role_name == u'':
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                        else:
                            query_set = query_set.filter(user__groups__name__icontains=role_name)
                            if service_area_name == u'':
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                            else:
                                query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)
                                if department_name == u'':
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                                else:
                                    query_set = query_set.filter(service_area_department__department_name__icontains=department_name)
                                    if name == u'':
                                        pass
                                    else:
                                        query_set = query_set.filter(user__name__icontains=name)
                    else:
                        pass
        return query_set

