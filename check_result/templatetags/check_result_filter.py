#coding=utf-8

from django import template
from django.template.defaultfilters import stringfilter
from hchq.untils import gl
import re
register = template.Library()

@register.filter
@stringfilter
def local(value):
    value_list = value.split()
    value = u''
    #print value_list
    for i in value_list:
        if gl.check_result_local.has_key(i):
            key_value = gl.check_result_local[i]
            if key_value:
                if i == value_list[-1]:
                    value += key_value
                else:
                    value += key_value + u'|'
        else:
            if i == value_list[-1]:
                if re.match(gl.check_result_pregnant_number_re_pattern, i):
                    value += i + u'周'
                else:
                    value += u'未知结果 '
            else:
                if re.match(gl.check_result_pregnant_number_re_pattern, i):
                    value += i + u'周|'
                else:
                    value += u'未知结果 |'

    if not value:
        value = u'未知结果'
    
    return value
