#coding=utf-8
from django import template
register = template.Library()

@register.inclusion_tag("tags/service_area_table_preview.html")
def service_area_table_preview(results_page):
    return {'results_page': results_page }
