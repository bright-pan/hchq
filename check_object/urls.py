from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.check_object.views',

       (r'add/(?P<check_object_page>\d{1,4})/$',
       'check_object_add',
       {'template_name' : 'check_object/check_object_add.html', 'next': '/check_object/person_management', },
       'check_object_add'),
       (r'add/uploader/$',
       'check_object_add_uploader',
       {'template_name' : 'check_object/check_object_add.html', 'next': '/check_object/person_management', },
       'check_object_add_uploader'),
                       
       (r'show/(?P<check_object_index>\d{1,4})/$',
       'check_object_show',
       {'template_name' : 'check_object/check_object_show.html', 'next': '', },
       'check_object_show'),

       (r'modify/(?P<check_object_page>\d{1,4})/$',
       'check_object_modify',
       {'template_name' : 'check_object/check_object_modify.html', 'next_template_name': 'check_object/check_object_detail_modify.html', },
       'check_object_modify'),

       (r'delete/(?P<check_object_page>\d{1,4})/$',
       'check_object_delete',
       {'template_name' : 'check_object/check_object_delete.html', 'next': '/check_object/person_management', },
       'check_object_delete'),

       (r'list/(?P<check_object_page>\d{1,4})/$',
       'check_object_list',
       {'template_name' : 'check_object/check_object_list.html', 'next': '/check_object/person_management', },
       'check_object_list'),

       (r'detail_modify/$',
       'check_object_detail_modify',
       {'template_name' : 'check_object/check_object_detail_modify.html', 'next': 'check_object/modify/1', },
       'check_object_detail_modify'),
                        
) 

