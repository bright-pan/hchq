#coding=utf-8
from django.conf.urls import patterns, include, url

urlpatterns = patterns('check_project.views',

       (r'add/(?P<check_project_page>\d{1,4})/$',
       'check_project_add',
       {'template_name' : 'check_project/check_project_add.html', 'next': '/account/person_management', },
       'check_project_add'),
                       
       (r'show/(?P<check_project_index>\d{1,4})/$',
       'check_project_show',
       {'template_name' : 'check_project/check_project_show.html', 'next': '', },
       'check_project_show'),

       (r'modify/(?P<check_project_page>\d{1,4})/$',
       'check_project_modify',
       {'template_name' : 'check_project/check_project_modify.html', 'next_template_name': 'check_project/check_project_detail_modify.html', },
       'check_project_modify'),

       (r'delete/(?P<check_project_page>\d{1,4})/$',
       'check_project_delete',
       {'template_name' : 'check_project/check_project_delete.html', 'next': '/account/person_management', },
       'check_project_delete'),

       (r'list/(?P<check_project_page>\d{1,4})/$',
       'check_project_list',
       {'template_name' : 'check_project/check_project_list.html', 'next': '/account/person_management', },
       'check_project_list'),

       (r'detail_modify/$',
       'check_project_detail_modify',
       {'template_name' : 'check_project/check_project_detail_modify.html', 'next': 'check_project/modify/1', },
       'check_project_detail_modify'),


#      (r'login$', 'login', {'template_name' : 'account/login.html', 'next': '/account/person_management', }, 'account_login'),
#      (r'logout$', 'exit', {'template_name' : 'account/login.html', 'next': '/', }, 'account_logout'),
#      (r'person_management$', 'person_management', {'template_name' : 'account/person_management.html', 'next': '/', }, 'account_person_management'),
#      (r'person_password_modify$', 'person_password_modify', {'template_name' : 'account/person_password_modify.html', 'next': '/', }, 'account_person_password_modify'),
                        
)

