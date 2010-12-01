#coding=utf-8
from django.utils.translation import ugettext_lazy as _

username_error_messages={'required': _(u'用户名称不能为空！'),
                         'max_length': _(u'用户名称长度大于30个字符！'),
                         'do_not_exist': _(u'用户名称不存在！'),
                         'format_error': _(u'用户名称必须由汉字，大小写字母，数字单独或者混合组成！'),
                         }
password_error_messages={'required': _(u'此处密码不能为空！'),
                         'max_length': _(u'密码长度大于30个字符！'),
                         'password_error': _(u'密码不正确！'),
                         'format_error':_(u'密码必须由大小写字母，数字单独或者混合组成！'),
                         'password_confirm_error': _(u'输入的新密码不一致，请重新输入！'),
                         'password_form_error': _(u'修改密码表单严重错误！'),
                         }
username_re_pattern = ur'^[\u4e00-\u9fa5\w]+$'
password_re_pattern = ur'^[\w]+$'