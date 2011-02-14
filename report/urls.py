#% -*- coding: utf-8 -*-
#coding=utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.report.views',

       (r'statistics/$',
       'report_statistics',
        {'template_name' : 'report/report_statistics.html', 'next': '/', },
       'report_statistics'),

)
