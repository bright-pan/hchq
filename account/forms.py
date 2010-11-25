#coding=utf-8
from django import forms

class login_form(forms.Form):
    username_error_messages={'required': u'你没有输入用户名称！',
                             'max_length': u'你输入大于10个汉字！',
                             'do_not_exist': u'你所输入的用户不存在！',
                             }, 
    username = forms.CharField(
        max_length=20,
        required=True, 
        label=u'用户名称', 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'20',}), 
        help_text=u'例如：潘聪',
        error_messages = username_error_messages,
    )
    password = forms.CharField(max_length=20)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
