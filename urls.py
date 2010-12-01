from django.conf.urls.defaults import *

from hchq import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('hchq.account.views',
    # Example:
    (r'^$', 'my_layout_test', {'template_name' : 'my.html'}, 'hchq_index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',

      (r'^account/', include('hchq.account.urls')),
#      (r'^account/logout$', logout, {'template_name' : 'account/logout.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
                        
)

urlpatterns += patterns('',

      (r'^service_area/', include('hchq.service_area.urls')),
#      (r'^account/logout$', logout, {'template_name' : 'account/logout.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
                        
)

urlpatterns += patterns('',
                        
      (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT}),
                        
)

urlpatterns += patterns('',
                        
      (r'^sentry/', include('sentry.urls')),
                        
)
