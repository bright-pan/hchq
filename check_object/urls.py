from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.check_object.views',

       (r'add/(?P<check_object_page>\d{1,8})/$',
       'check_object_add',
       {'template_name' : 'check_object/check_object_add.html', 'next': 'check_object/list/1', },
       'check_object_add'),
       (r'add/uploader/$',
       'check_object_add_uploader',
       {'template_name' : 'check_object/check_object_add.html', 'next': '/check_object/person_management', },
       'check_object_add_uploader'),

       (r'add/camera/$',
       'check_object_add_camera',
       {'template_name' : 'check_object/check_object_add.html', 'next': '/check_object/person_management', },
       'check_object_add_camera'),

       (r'detail_modify/uploader/$',
       'check_object_detail_modify_uploader',
       {'template_name' : 'check_object/check_object_add.html', 'next': '/check_object/person_management', },
       'check_object_detail_modify_uploader'),
                       
       (r'detail_modify/camera/$',
       'check_object_detail_modify_camera',
       {'template_name' : 'check_object/check_object_add.html', 'next': '/check_object/person_management', },
       'check_object_detail_modify_camera'),
                       
       (r'show/(?P<check_object_index>\d{1,8})/(?P<success>\w+)/$',
       'check_object_show',
       {'template_name' : 'check_object/check_object_show.html', 'next': '', },
       'check_object_show'),

       (r'modify/(?P<check_object_page>\d{1,8})/$',
       'check_object_modify',
       {'template_name' : 'check_object/check_object_modify.html', 'next_template_name': 'check_object/check_object_detail_modify.html', },
       'check_object_modify'),

       (r'delete/(?P<check_object_page>\d{1,8})/$',
       'check_object_delete',
       {'template_name' : 'check_object/check_object_delete.html', 'next': '/check_object/person_management', },
       'check_object_delete'),

       (r'list/(?P<check_object_page>\d{1,8})/$',
       'check_object_list',
       {'template_name' : 'check_object/check_object_list.html', 'next': '/check_object/person_management', },
       'check_object_list'),
                       
       (r'invalid/(?P<check_object_page>\d{1,8})/$',
       'check_object_invalid',
       {'template_name' : 'check_object/check_object_invalid.html', 'next': '/check_object/person_management', },
       'check_object_invalid'),

       (r'detail_modify/$',
       'check_object_detail_modify',
       {'template_name' : 'check_object/check_object_detail_modify.html', 'next': 'check_object/modify/1', },
       'check_object_detail_modify'),

) 

