#coding=utf-8
from django.utils.translation import ugettext_lazy as _

username_error_messages={'required': _(u'用户名称不能为空！'),
                         'max_length': _(u'用户名称长度大于30个字符！'),
                         'do_not_exist': _(u'用户名称不存在！'),
                         'format_error': _(u'用户名称必须由汉字，大小写字母，数字单独或者混合组成！'),
                         'form_error': _(u'表单严重错误！'),
                         }

password_error_messages={'required': _(u'此处密码不能为空！'),
                         'max_length': _(u'密码长度大于30个字符！'),
                         'password_error': _(u'密码不正确！'),
                         'format_error':_(u'密码必须由大小写字母，数字单独或者混合组成！'),
                         'password_confirm_error': _(u'输入的新密码不一致，请重新输入！'),
                         'form_error': _(u'修改密码表单严重错误！'),
                         }
username_re_pattern = ur'^[\u4e00-\u9fa5\w]+$'
password_re_pattern = ur'^[\w]+$'

service_area_name_error_messages={'required': _(u'请输入服务区域名称！'),
                                  'max_length': _(u'输入的服务区域名称长度大于500个字符！'),
                                  'format_error': _(u'服务区域名称必须是汉字组成，并且多个服务区名称使用/字符分隔！'),
                                  'form_error': _(u'表单严重错误！'),
                                  'already_error': _(u'服务区域同名，请输入正确的服务区域名称！'),
                                  }

service_area_name_add_re_pattern = ur'^[\u4e00-\u9fa5/]+$'
service_area_name_modify_re_pattern = ur'^[\u4e00-\u9fa5]+$'
#service_area_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$'
service_area_name_search_re_pattern = ur'(^[\u4e00-\u9fa5]+$)|(^$)'

def filter_null_string(n):
    return len(n) > 0

session_service_area_name = u'session_service_area_name'
session_service_area_is_fuzzy = u'session_service_area_is_fuzzy'

department_name_error_messages={'required': _(u'请输入部门单位名称！'),
                                  'max_length': _(u'输入的部门单位名称长度大于500个字符！'),
                                  'format_error': _(u'部门单位名称必须是汉字组成，并且多个服务区名称使用/字符分隔！'),
                                  'form_error': _(u'表单严重错误！'),
                                  'already_error': _(u'部门单位同名，请输入正确的部门单位名称！'),
                                  }

department_name_add_re_pattern = ur'^[\u4e00-\u9fa5/]+$'
department_name_modify_re_pattern = ur'^[\u4e00-\u9fa5]+$'
#department_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$'
department_name_search_re_pattern = ur'(^[\u4e00-\u9fa5]+$)|(^$)'

session_department_name = u'session_department_name'
session_department_is_fuzzy = u'session_department_is_fuzzy'
