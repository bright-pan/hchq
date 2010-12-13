from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.account.views',
                        
      (r'login/$', 'login', {'template_name' : 'account/login.html', 'next': '/account/person_management', }, 'account_login'),
      (r'logout/$', 'exit', {'template_name' : 'account/login.html', 'next': '/', }, 'account_logout'),
      (r'person_management/$', 'person_management', {'template_name' : 'account/person_management.html', 'next': '/', }, 'account_person_management'),
      (r'person_password_modify/$', 'person_password_modify', {'template_name' : 'account/person_password_modify.html', 'next': '/', }, 'account_person_password_modify'),
#      (r'^account/logout$', logout, {'template_name' : 'account/logout.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
                        
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

#       (r'role_limit_add/(?P<role_index>\d{1,4})/(?P<role_limit_page>\d{1,4})/$',
#       'role_limit_add',
#       {'template_name' : 'account/role/role_limit_add.html', 'next': '/account/person_management', },
#       'account_role_limit_add'),
                       
#       (r'role_limit_delete/(?P<role_index>\d{1,4})/(?P<role_limit_page>\d{1,4})/$',
#       'role_limit_delete',
#       {'template_name' : 'account/role/role_limit_delete.html', 'next': '/account/person_management', },
#       'account_role_limit_delete'),

#       (r'role_limit_list/(?P<role_index>\d{1,4})/(?P<role_limit_page>\d{1,4})/$',
#       'role_limit_list',
#       {'template_name' : 'account/role/role_limit_list.html', 'next': '/account/person_management', },
#       'account_role_limit_list'),

)

