#% -*- coding: utf-8 -*-
#coding=utf-8
from django.conf.urls import patterns, include, url

urlpatterns = patterns('report.views',

       (r'check_or_not/$',
       'report_check_or_not',
        {'template_name' : 'report/report_check_or_not.html', 'next': '/', },
       'report_check_or_not'),

       (r'statistics/$',
       'report_statistics',
        {'template_name' : 'report/report_statistics.html', 'next': '/', },
       'report_statistics'),

) 

