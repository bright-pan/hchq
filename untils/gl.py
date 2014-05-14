#coding=utf-8
from django.utils.translation import ugettext_lazy as _
############################################################
#系统用户表单
############################################################
account_name_error_messages={'required': _(u'用户名称不能为空！'),
                         'max_length': _(u'用户名称长度大于30个字符！'),
                         'do_not_exist': _(u'用户名称不存在！'),
                         'format_error': _(u'用户名称必须由汉字，大小写字母，数字单独或者混合组成！'),
                         'form_error': _(u'表单严重错误！'),
                         'already_error':_(u'用户名已存在！'),
                         }

account_password_error_messages={'required': _(u'此处密码不能为空！'),
                         'max_length': _(u'密码长度大于30个字符！'),
                         'password_error': _(u'密码不正确！'),
                         'format_error':_(u'密码必须由大小写字母，数字单独或者混合组成！'),
                         'password_confirm_error': _(u'输入的新密码不一致，请重新输入！'),
                         'form_error': _(u'修改密码表单严重错误！'),
                         }
account_name_re_pattern = ur'^[\u4e00-\u9fa5\w]+$'
account_name_search_re_pattern = ur'^[\u4e00-\u9fa5\w]+$|(^$)'
account_name_add_re_pattern = ur'^[\u4e00-\u9fa5\w]+$'

account_password_re_pattern = ur'^[\w]+$'
################################################################################
#服务区域表单
################################################################################

service_area_name_error_messages={'required': _(u'请输入服务区域名称！'),
                                  'max_length': _(u'输入的服务区域名称长度大于500个字符！'),
                                  'format_error': _(u'服务区域名称必须是汉字组成，并且多个服务区名称使用/字符分隔！'),
                                  'form_error': _(u'表单严重错误！'),
                                  'already_error': _(u'服务区域同名，请输入正确的服务区域名称！'),
                                  'not_exist_error': _(u'服务区域不存在'),
                                  }
service_area_name_add_re_pattern = ur'^[\u4e00-\u9fa5/()（）、]+$'
service_area_name_modify_re_pattern = ur'^[\u4e00-\u9fa5()（）、]+$'
#service_area_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$'
service_area_name_search_re_pattern = ur'(^[\u4e00-\u9fa5()（）、]+$)|(^$)'

#过滤器
def filter_null_string(n):
    return len(n) > 0

session_service_area_name = u'session_service_area_name'
session_service_area_is_fuzzy = u'session_service_area_is_fuzzy'
################################################################################
#单位部门表单
################################################################################
department_name_error_messages={'required': _(u'请输入单位部门名称！'),
                                'max_length': _(u'输入的单位部门名称长度大于500个字符！'),
                                'format_error': _(u'单位部门名称必须是汉字组成，并且多个服务区名称使用/字符分隔！'),
                                'form_error': _(u'表单严重错误！'),
                                'already_error': _(u'单位部门同名，请输入正确的单位部门名称！'),
                                'not_exist_error': _(u'单位部门不存在'),
                                'not_match_error': _(u'服务区域与单位部门未关联！'),
                                  }

department_name_add_re_pattern = ur'^[\u4e00-\u9fa5/()（）、]+$'
department_name_modify_re_pattern = ur'^[\u4e00-\u9fa5()（）、]+$'
#department_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$'
department_name_search_re_pattern = ur'(^[\u4e00-\u9fa5()（）、]+$)|(^$)'

session_department_name = u'session_department_name'
session_department_is_fuzzy = u'session_department_is_fuzzy'

session_service_area_department_name = u'session_service_area_department_name'
session_service_area_department_is_fuzzy = u'session_service_area_department_is_fuzzy'
################################################################################
#角色表单
################################################################################
role_name_error_messages={'required': _(u'请输入角色名称！'),
                          'max_length': _(u'输入的角色名称长度大于500个字符！'),
                          'format_error': _(u'角色名称必须是汉字组成，并且多个服务区名称使用/字符分隔！'),
                          'form_error': _(u'表单严重错误！'),
                          'already_error': _(u'角色同名，请输入正确的角色名称！'),
                          'not_exist_error': _(u'角色不存在'),
                                  }
permission_name_error_messages={'required': _(u'请输入权限名称！'),
                                  'max_length': _(u'输入的权限名称长度大于500个字符！'),
                                  'format_error': _(u'权限名称必须是汉字组成，并且多个服务区名称使用/字符分隔！'),
                                  'form_error': _(u'表单严重错误！'),
                                  'already_error': _(u'权限同名，请输入正确的权限名称！'),
                                  }

role_name_add_re_pattern = ur'^[\u4e00-\u9fa5/]+$'
role_name_modify_re_pattern = ur'^[\u4e00-\u9fa5]+$'
#role_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$'
role_name_search_re_pattern = ur'(^[\u4e00-\u9fa5]+$)|(^$)'
permission_name_add_re_pattern = ur'^[\u4e00-\u9fa5/]+$'
permission_name_modify_re_pattern = ur'^[\u4e00-\u9fa5]+$'
#permission_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$'
permission_name_search_re_pattern = ur'(^[\u4e00-\u9fa5]+$)|(^$)'

session_role_name = u'session_role_name'
session_role_is_fuzzy = u'session_role_is_fuzzy'

session_role_permission_name = u'session_role_permission_name'
session_role_permission_is_fuzzy = u'session_role_permission_is_fuzzy'

################################################################################
#检查项目表单
################################################################################
check_project_name_error_messages={'required': _(u'请输入检查项目名称！'),
                                   'max_length': _(u'输入的检查项目名称长度大于64个字符！'),
                                   'format_error': _(u'检查项目名称必须是汉字、数字以及-组成！'),
                                   'form_error': _(u'表单严重错误！'),
                                   'already_error': _(u'检查项目同名，请输入正确的检查项目名称！'),
                                   }
check_project_time_error_messages={'required': _(u'请输入时间！'),
                                   'invalid': _(u'输入的时间格式不正确！'),
                                   'logic_error': _(u'输入的开始时间在结束时间之前！'),
                                   'form_error': _(u'表单严重错误'),
                                   }

check_project_name_add_re_pattern = ur'^[\u4e00-\u9fa5\d-]+$'#汉字和数字著称
check_project_name_modify_re_pattern = ur'^[\u4e00-\u9fa5\d-]+$'
check_project_name_search_re_pattern = ur'(^[\u4e00-\u9fa5\d-]+$)|(^$)'

session_check_project_name = u'session_check_project_name'
session_check_project_start_time = u'session_check_project_start_time'
session_check_project_end_time = u'session_check_project_end_time'
session_check_project_is_fuzzy = u'session_check_project_is_fuzzy'

################################################################################
#用户表单
################################################################################
session_account_name = u'session_account_name'
session_account_service_area_name = u'session_account_service_area_name'
session_account_department_name = u'session_account_department_name'
session_account_role_name = u'session_account_role_name'
session_account_is_checker = u'session_account_is_checker'
session_account_is_fuzzy = u'session_account_is_fuzzy'
################################################################################
#检查对象表单
################################################################################

check_object_name_search_re_pattern = ur'^[\u4e00-\u9fa5]+$|(^$)'
check_object_name_add_re_pattern = ur'^[\u4e00-\u9fa5]+$'

check_object_id_number_search_re_pattern = ur'^[\dxX]+$|(^$)'
check_object_id_number_add_re_pattern = ur'(^[\d]{15}$)|([\d]{17}[\dxX]{1})|(^$)'

check_object_name_error_messages={'required': _(u'请输入检查对象名称！'),
                                   'max_length': _(u'输入的检查对象名称长度大于64个字符！'),
                                   'format_error': _(u'检查对象名称必须是汉字！'),
                                   'form_error': _(u'表单严重错误！'),
                                   'already_error': _(u'检查对象同名，请输入正确的检查对象名称！'),
                                   }
check_object_id_number_error_messages={'required': _(u'请输入身份证号码名称！'),
                                       'max_length': _(u'输入的身份证号码名称长度大于18个字符！'),
                                       'format_error': _(u'该字段必须是15位数字或者18位的身份证'),
                                       'form_error': _(u'表单严重错误！'),
                                       'already_error': _(u'身份证号码同名，请输入正确的身份证号码！'),
                                   }

check_object_ctp_method_time_error_messages={'required': _(u'请输入时间！'),
                                             'invalid': _(u'输入的时间格式不正确！'),
                                             'logic_error': _(u'输入的时间必须在今天之前！'),
                                             'form_error': _(u'表单严重错误'),
                                             }

check_object_wedding_time_error_messages={'required': _(u'请输入时间！'),
                                          'invalid': _(u'输入的时间格式不正确！'),
                                          'logic_error': _(u'输入的时间必须在今天之前！'),
                                          'form_error': _(u'表单严重错误'),
                                          }


check_object_image_size = (208,156)#宽/高
check_object_thumbnail_size = (47, 41)
#check_object_id_mark_color = (39, 96, 137)
#check_object_id_mark_bottom_color = (204,223,243)
check_object_rect_mark = (0,140)#宽/高
check_object_rect_mark_color = (0,45,0)
check_object_text_mark = (check_object_rect_mark[0]+16, check_object_rect_mark[1])
check_object_text_mark_color = (255,255,255)

session_check_object_name = u'session_check_object_name'
session_check_object_id_number = u'session_check_object_id_number'
session_check_object_service_area_name = u'session_check_object_service_area_name'
session_check_object_department_name = u'session_check_object_department_name'
session_check_object_is_family = u'session_check_object_is_family'
session_check_object_mate_name = u'session_check_object_mate_name'
session_check_object_mate_id_number = u'session_check_object_mate_id_number'
session_check_object_mate_service_area_name = u'session_check_object_mate_service_area_name'
session_check_object_mate_department_name = u'session_check_object_mate_department_name'
session_check_object_is_fuzzy = u'session_check_object_is_fuzzy'
session_check_object_ctp_method = u'session_check_object_ctp_method'
session_check_object_del_reason = u'session_check_object_del_reason'
session_check_object_ctp_method_time = u'session_check_object_ctp_method_time'
session_check_object_wedding_time = u'session_check_object_wedding_time'
session_check_object_modify_start_time = u'session_check_object_modify_start_time'
session_check_object_modify_end_time = u'session_check_object_modify_end_time'

session_check_object_detail_modify_uploader = u'session_check_object_detail_modify_uploader'
session_check_object_detail_modify_id_number = u'session_check_object_detail_modify_id_number'

check_object_ctp_local = {u'method_0':u'未使用',
                          u'method_1':u'避孕环方式',
                          u'method_2':u'避孕药方式',
                          u'method_3':u'其他方式',
                      }

check_object_del_reason = {u'del_reason_1':u'离婚删除',
                          u'del_reason_2':u'调离删除',
                          u'del_reason_3':u'超龄删除',
                          u'del_reason_4':u'因病致绝育删除',
                          u'del_reason_5':u'其他原因删除',
                          }
#check_object_init_flag = False
################################################

#################################################

session_check_result_pregnant = u'session_check_result_pregnant'
session_check_result_special = u'session_check_result_special'
session_check_result_ring = u'session_check_result_ring'
session_check_result_pregnant_period = u'session_check_result_pregnant_period'
session_check_result_checker = u'session_check_result_checker'
session_check_result_recorder = u'session_check_result_recorder'
session_check_result_check_project = u'session_check_result_check_project'
session_check_result_start_time = u'session_check_result_start_time'
session_check_result_end_time = u'session_check_result_end_time'

check_result_local = {u'None':u'',
                      u'invalid':u'本次失效',
                      u'pregnant':u'有孕',
                      u'unpregnant':u'无孕',
                      u'ring':u'有环',
                      u'unring':u'无环',
                      u'special_1':u'生小孩子三个月内',
                      u'special_2':u'生病住院',
                      u'special_3':u'其他原因',
                      u'special_4':u'单位担保',
                      u'special_5':u'医学手术证明',
                      u'special_6':u'外地环孕检证明',
                      }

check_result_pregnant_number_re_pattern = ur'(^[\d]{2}$)|(^[\d]{1}$)'

