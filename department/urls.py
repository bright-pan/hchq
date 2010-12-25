#coding=utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.department.views',

      (r'add/(?P<department_page>\d{1,4})/$',
       'department_add',
       {'template_name' : 'department/department_add.html', 'next': '/account/person_management', },
       'department_add'),
                       
      (r'show/(?P<department_index>\d{1,4})/$',
       'department_show',
       {'template_name' : 'department/department_show.html', 'next': '', },
       'department_show'),

      (r'modify/(?P<department_page>\d{1,4})/$',
       'department_modify',
       {'template_name' : 'department/department_modify.html', 'next': '/account/person_management', },
       'department_modify'),

       (r'delete/(?P<department_page>\d{1,4})/$',
       'department_delete',
       {'template_name' : 'department/department_delete.html', 'next': '/account/person_management', },
       'department_delete'),

       (r'list/(?P<department_page>\d{1,4})/$',
       'department_list',
       {'template_name' : 'department/department_list.html', 'next': '/account/person_management', },
       'department_list'),

       (r'department_name_ajax/$',
       'department_name_ajax',
       {'template_name' : 'department/department_department_list.html', 'next': '/account/person_management', },
       'department_name_ajax'),

#      (r'login$', 'login', {'template_name' : 'account/login.html', 'next': '/account/person_management', }, 'account_login'),
#      (r'logout$', 'exit', {'template_name' : 'account/login.html', 'next': '/', }, 'account_logout'),
#      (r'person_management$', 'person_management', {'template_name' : 'account/person_management.html', 'next': '/', }, 'account_person_management'),
#      (r'person_password_modify$', 'person_password_modify', {'template_name' : 'account/person_password_modify.html', 'next': '/', }, 'account_person_password_modify'),
                        
)

