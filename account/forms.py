#coding=utf-8
from django import forms

class login_form(forms.Form):
    username = forms.CharField(
        error_messages={'required': u'你没有输入用户名称！',
                        'max_length': u'你输入大于10个汉字！',
                        }, 
        max_length=20,
        required=True, 
        label=u'用户名称', 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'20',}), 
        help_text=u'例如：潘聪'),
    )
    password = forms.CharField(max_length=20)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
