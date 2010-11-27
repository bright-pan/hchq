#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class login_form(forms.Form):
    """
    用户登入表单
    """
    user = None
    username_error_messages={'required': _(u'请输入用户名称！'),
                             'max_length': _(u'输入的用户名称长度大于10个汉字！'),
                             'do_not_exist': _(u'你所输入的用户不存在！'),
                             }
    password_error_messages={'required': _(u'请输入用户密码！'),
                             'max_length': _(u'输入的用户密码长度大于10个汉字！'),
                             'password_error': _(u'输入的用户密码不正确，请重新输入！'),
                             }

    username = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'用户名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：张三'),
        error_messages = username_error_messages,
    )
    password = forms.CharField(
        max_length=30,
        required=True, 
        label=_(u'用户密码'), 
        widget=forms.PasswordInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：123456'),
        error_messages = password_error_messages,
    )
    
    def clean_username(self):
        try:
            username = self.cleaned_data.get('username')
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError(self.username_error_messages['do_not_exist'])
        return username

    def clean_password(self):

        try:
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
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
        
