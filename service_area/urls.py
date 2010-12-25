#coding=utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.service_area.views',

      (r'add/(?P<service_area_page>\d{1,4})/$',
       'service_area_add',
       {'template_name' : 'service_area/service_area_add.html', 'next': '/account/person_management', },
       'service_area_add'),
                       
      (r'show/(?P<service_area_index>\d{1,4})/$',
       'service_area_show',
       {'template_name' : 'service_area/service_area_show.html', 'next': '', },
       'service_area_show'),

      (r'modify/(?P<service_area_page>\d{1,4})/$',
       'service_area_modify',
       {'template_name' : 'service_area/service_area_modify.html', 'next': '/account/person_management', },
       'service_area_modify'),

       (r'delete/(?P<service_area_page>\d{1,4})/$',
       'service_area_delete',
       {'template_name' : 'service_area/service_area_delete.html', 'next': '/account/person_management', },
       'service_area_delete'),

       (r'list/(?P<service_area_page>\d{1,4})/$',
       'service_area_list',
       {'template_name' : 'service_area/service_area_list.html', 'next': '/account/person_management', },
       'service_area_list'),

       (r'department_add/(?P<service_area_index>\d{1,4})/(?P<service_area_department_page>\d{1,4})/$',
       'service_area_department_add',
       {'template_name' : 'service_area/service_area_department_add.html', 'next': '/account/person_management', },
       'service_area_department_add'),
                       
       (r'department_delete/(?P<service_area_index>\d{1,4})/(?P<service_area_department_page>\d{1,4})/$',
       'service_area_department_delete',
       {'template_name' : 'service_area/service_area_department_delete.html', 'next': '/account/person_management', },
       'service_area_department_delete'),

       (r'department_list/(?P<service_area_index>\d{1,4})/(?P<service_area_department_page>\d{1,4})/$',
       'service_area_department_list',
       {'template_name' : 'service_area/service_area_department_list.html', 'next': '/account/person_management', },
       'service_area_department_list'),

       (r'service_area_name_ajax/$',
       'service_area_name_ajax',
       {'template_name' : 'service_area/service_area_department_list.html', 'next': '/account/person_management', },
       'service_area_name_ajax'),
#      (r'login$', 'login', {'template_name' : 'account/login.html', 'next': '/account/person_management', }, 'account_login'),
#      (r'logout$', 'exit', {'template_name' : 'account/login.html', 'next': '/', }, 'account_logout'),
#      (r'person_management$', 'person_management', {'template_name' : 'account/person_management.html', 'next': '/', }, 'account_person_management'),
#      (r'person_password_modify$', 'person_password_modify', {'template_name' : 'account/person_password_modify.html', 'next': '/', }, 'account_person_password_modify'),
                        
)

