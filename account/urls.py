from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.account.views',
                        
      (r'login/$', 'login', {'template_name' : 'account/login.html', 'next': '/account/person_management',}, 'account_login'),
      (r'logout/$', 'exit', {'template_name' : 'account/login.html', 'next': '/', }, 'account_logout'),
      (r'person_management/$', 'person_management', {'template_name' : 'account/person_management.html', 'next': '/', }, 'account_person_management'),
      (r'person_password_modify/$', 'person_password_modify', {'template_name' : 'account/person_password_modify.html', 'next': '/account/person_management', }, 'account_person_password_modify'),
#      (r'^account/logout$', logout, {'template_name' : 'account/logout.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
       (r'get_bar_chart/',
       'get_bar_chart',
        {'template_name' : 'index.html', 'next': '/account/person_management', },
       'get_bar_chart'),
       (r'get_pie_chart/',
       'get_pie_chart',
        {'template_name' : 'index.html', 'next': '/account/person_management', },
       'get_pie_chart'),
       (r'get_dot_chart/',
       'get_dot_chart',
        {'template_name' : 'index.html', 'next': '/account/person_management', },
       'get_dot_chart'),
)
urlpatterns += patterns('hchq.account.views',

      (r'role_add/(?P<role_page>\d{1,4})/$',
       'role_add',
       {'template_name' : 'account/role/role_add.html', 'next': '/account/person_management', },
       'account_role_add'),
                       
#      (r'role_show/(?P<role_index>\d{1,4})/$',
#       'role_show',
#       {'template_name' : 'account/role/role_show.html', 'next': '', },
#       'account_role_show'),

      (r'role_modify/(?P<role_page>\d{1,4})/$',
       'role_modify',
       {'template_name' : 'account/role/role_modify.html', 'next': '/account/person_management', },
       'account_role_modify'),

       (r'role_delete/(?P<role_page>\d{1,4})/$',
       'role_delete',
       {'template_name' : 'account/role/role_delete.html', 'next': '/account/person_management', },
       'account_role_delete'),

       (r'role_list/(?P<role_page>\d{1,4})/$',
       'role_list',
       {'template_name' : 'account/role/role_list.html', 'next': '/account/person_management', },
       'account_role_list'),

       (r'role_permission_add/(?P<role_index>\d{1,4})/(?P<role_permission_page>\d{1,4})/$',
       'role_permission_add',
       {'template_name' : 'account/role/role_permission_add.html', 'next': '/account/person_management', },
        'account_role_permission_add'),
                       
       (r'role_permission_delete/(?P<role_index>\d{1,4})/(?P<role_permission_page>\d{1,4})/$',
       'role_permission_delete',
       {'template_name' : 'account/role/role_permission_delete.html', 'next': '/account/person_management', },
       'account_role_permission_delete'),

       (r'role_permission_list/(?P<role_index>\d{1,4})/(?P<role_permission_page>\d{1,4})/$',
       'role_permission_list',
       {'template_name' : 'account/role/role_permission_list.html', 'next': '/account/person_management', },
       'account_role_permission_list'),

       (r'role_name_ajax/',
       'role_name_ajax',
        {'template_name' : 'account/role/role_permission_list.html', 'next': '/account/person_management', },
       'role_name_ajax'),
)

urlpatterns += patterns('hchq.account.views',

       (r'add/(?P<account_page>\d{1,4})/$',
       'account_add',
       {'template_name' : 'account/management/account_add.html', 'next': '/account/person_management', },
       'account_add'),
                       
       (r'show/(?P<account_index>\d{1,4})/$',
       'account_show',
       {'template_name' : 'account/management/account_show.html', 'next': '', },
       'account_show'),

       (r'modify/(?P<account_page>\d{1,4})/$',
       'account_modify',
       {'template_name' : 'account/management/account_modify.html', 'next_template_name': 'account/management/account_detail_modify.html', },
       'account_modify'),

       (r'delete/(?P<account_page>\d{1,4})/$',
       'account_delete',
       {'template_name' : 'account/management/account_delete.html', 'next': '/account/person_management', },
       'account_delete'),

       (r'list/(?P<account_page>\d{1,4})/$',
       'account_list',
       {'template_name' : 'account/management/account_list.html', 'next': '/account/person_management', },
       'account_list'),

       (r'detail_modify/$',
       'account_detail_modify',
       {'template_name' : 'account/management/account_detail_modify.html', 'next': 'account/modify/1', },
       'account_detail_modify'),
                        
) 

