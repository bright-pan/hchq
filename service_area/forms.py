#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist

class ServiceAreaAddForm(forms.Form):
    """
    服务区域添加表单
    """
    service_area_name_error_messages={'required': _(u'请输入服务区域名称！'),
                             'max_length': _(u'输入的服务区域名称长度大于250个汉字！'),
                             'format_error': _(u'你所输入的用户不存在！'),
                             }
    
    service_area_name = forms.CharField(
        max_length=500,
        required=True, 
        label=_(u'服务区域名称'), 
        widget=forms.Textarea(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田乡/西江镇/文武坝乡/...'),
        error_messages = service_area_name_error_messages,
        )
    
    def clean_service_area_name(self):
        try:
            service_area_name = self.data.get('service_area_name')
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError(self.username_error_messages['do_not_exist'])
        return username

    def clean_password(self):

        try:
            username = self.data.get('username')
            password = self.data.get('password')
            from django.contrib.auth import authenticate
            self.user = authenticate(username = username, password = password)
            if self.user is None:
                raise forms.ValidationError(self.password_error_messages['password_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(self.username_error_messages['do_not_exist'])
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

    modify_password_error_messages={'required': _(u'请输入用户密码！'),
                                    'max_length': _(u'输入的用户密码长度大于10个汉字！'),
                                    'password_confirm_error': _(u'输入的新用户密码不一致，请重新输入！'),
                                    'password_form_error': _(u'修改密码表单严重错误！'),
                                    }

    password_new = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'新密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：123456'),
        error_messages = modify_password_error_messages,
        )
    password_confirm = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'确认新密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'请重新输入密码，例如：123456'),
        error_messages = modify_password_error_messages,
        )
    
    def clean_password_new(self):
        try:
            password_new_copy = self.data.get('password_new')
            password_confirm_copy = self.data.get('password_confirm')        
            if password_new_copy != password_confirm_copy:
                raise forms.ValidationError(self.modify_password_error_messages['password_confirm_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(self.modify_password_error_messages['password_form_error'])
        return password_new_copy

    def clean_password_confirm(self):
        try:
            password_new_copy = self.data.get('password_new')
            password_confirm_copy = self.data.get('password_confirm')        
            if password_new_copy != password_confirm_copy:
                raise forms.ValidationError(self.modify_password_error_messages['password_confirm_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(self.modify_password_error_messages['password_form_error'])
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

