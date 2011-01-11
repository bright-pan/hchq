#coding=utf-8

from django import template
from django.template.defaultfilters import stringfilter
from hchq.untils import gl

register = template.Library()

@register.filter
@stringfilter
def local(value):
    value_list = value.split()
    print value_list
    if gl.check_result_local.has_key(value_list[0]) and gl.check_result_local.has_key(value_list[1]) and len(value_list) == 3:
        if value_list[2] == u'None':
            return u'%s|%s' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]])
        else:
            return u'%s|%s|%s周' % (gl.check_result_local[value_list[0]], gl.check_result_local[value_list[1]], value_list[2])
    else:
        return u''
