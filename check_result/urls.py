from django.conf.urls import patterns, include, url

urlpatterns = patterns('check_result.views',

       (r'show/(?P<check_result_index>\d{1,8})/(?P<success>\w+)/$',
       'check_result_show',
       {'template_name' : 'check_result/check_result_show.html', 'next': '', },
       'check_result_show'),

       (r'add/(?P<check_object_page>\d{1,8})/$',
       'check_result_add',
       {'template_name' : 'check_result/check_result_add.html', 'next_template_name': 'check_result/check_result_detail_add.html', 'next_error':'check_result/check_result_detail_add_error.html'},
       'check_result_add'),

       (r'list/(?P<check_result_page>\d{1,8})/$',
       'check_result_list',
       {'template_name' : 'check_result/check_result_list.html', 'next': '/check_result/person_management', },
       'check_result_list'),

       (r'detail_add/$',
       'check_result_detail_add',
       {'template_name' : 'check_result/check_result_detail_add.html', 'next': 'check_result/add/1', },
       'check_result_detail_add'),

       (r'special/(?P<check_object_page>\d{1,8})/$',
       'check_result_special_add',
       {'template_name' : 'check_result/check_result_special_add.html', 'next_template_name': 'check_result/check_result_special_detail_add.html', 'next_error':'check_result/check_result_detail_add_error.html'},
       'check_result_special_add'),

       (r'special_detail/$',
       'check_result_special_detail_add',
       {'template_name' : 'check_result/check_result_special_detail_add.html', 'next': 'check_result/add/1', },
       'check_result_special_detail_add'),
                       
) 

