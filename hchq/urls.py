from django.conf.urls import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('account.views',
                       # Example:
                       (r'^$', 'my_layout_test', {'template_name' : 'my_index.html'}, 'hchq_index'),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       (r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
                        (r'^account/', include('account.urls')),

)

urlpatterns += patterns('',
                        (r'^service_area/', include('service_area.urls')),
)
urlpatterns += patterns('',
                        (r'^department/', include('department.urls')),
)

urlpatterns += patterns('',
                        (r'^check_project/', include('check_project.urls')),
)

urlpatterns += patterns('',
                        (r'^check_object/', include('check_object.urls')),
)

urlpatterns += patterns('',
                        (r'^check_result/', include('check_result.urls')),
)

urlpatterns += patterns('',
                        (r'^report/', include('report.urls')),
)

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
#urlpatterns += patterns('',

#      (r'^sentry/', include('sentry.urls')),

#)
