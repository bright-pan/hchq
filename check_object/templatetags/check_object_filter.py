#coding=utf-8

from django import template
from django.template.defaultfilters import stringfilter
from untils import gl

register = template.Library()

@register.filter
@stringfilter
def ctp_local(value):
    
    if gl.check_object_ctp_local.has_key(value):
        return u'%s' % gl.check_object_ctp_local[value]
    else:
        return u''


@register.filter
@stringfilter
def del_reason_local(value):
    if gl.check_object_del_reason.has_key(value):
        return u'%s' % gl.check_object_del_reason[value]
    else:
        return u''

@register.filter
@stringfilter
def image_url_local(value):
    import random
    return value + "?" + "".join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10))

