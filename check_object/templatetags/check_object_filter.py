#coding=utf-8

from django import template
from django.template.defaultfilters import stringfilter
from hchq.untils import gl

register = template.Library()

@register.filter
@stringfilter
def ctp_local(value):
    
    if gl.check_object_ctp_local.has_key(value):
        return u'%s' % gl.check_object_ctp_local[value]
    else:
        return u''
