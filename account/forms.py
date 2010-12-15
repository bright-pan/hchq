#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist

from hchq.untils import gl

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
        error_messages = gl.username_error_messages,
        )
    password = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'用户密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                          'size':'30',}), 
        help_text=_(u'例如：123456, pa123456'),
        error_messages = gl.password_error_messages,
        )
    
    def clean_username(self):
        try:
            username = self.data.get('username')
            if re.match(gl.username_re_pattern, username ) is None:
                raise forms.ValidationError(gl.username_error_messages['format_error'])
            User.objects.get(username=username, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.username_error_messages['do_not_exist'])
        return username

    def clean_password(self):

        try:
            username = self.data.get('username')
            password = self.data.get('password')
            if re.match(gl.password_re_pattern, password ) is None:
                raise forms.ValidationError(gl.password_error_messages['format_error'])
            from django.contrib.auth import authenticate
            self.user = authenticate(username = username, password = password)
            if self.user is None:
                raise forms.ValidationError(gl.password_error_messages['password_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.username_error_messages['do_not_exist'])
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
        error_messages = gl.password_error_messages,
        )
    password_confirm = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'确认新密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                          'size':'30',}), 
        help_text=_(u'请重新输入密码，例如：123456, pa123456'),
        error_messages = gl.password_error_messages,
        )
    
    def clean_password_new(self):
        try:
            password_new_copy = self.data.get('password_new')
            if re.match(gl.password_re_pattern, password_new_copy ) is None:
                raise forms.ValidationError(gl.password_error_messages['format_error'])
            password_confirm_copy = self.data.get('password_confirm')        
            if password_new_copy != password_confirm_copy:
                raise forms.ValidationError(self.password_error_messages['password_confirm_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(self.password_error_messages['password_form_error'])
        return password_new_copy

    def clean_password_confirm(self):
        try:
            password_new_copy = self.data.get('password_new')
            password_confirm_copy = self.data.get('password_confirm')        
            if re.match(gl.password_re_pattern, password_confirm_copy ) is None:
                raise forms.ValidationError(gl.password_error_messages['format_error'])
            if password_new_copy != password_confirm_copy:
                raise forms.ValidationError(gl.password_error_messages['password_confirm_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.password_error_messages['form_error'])
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
