from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.account.views',
                        
      (r'login$', 'login', {'template_name' : 'account/login.html'}),
      (r'logout$', 'exit', {'template_name' : 'account/login.html'}),                        
#      (r'^account/logout$', logout, {'template_name' : 'account/logout.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
                        
)

urlpatterns += patterns('django.contrib.auth.views',
                        
#      (r'login$', 'login', {'template_name' : 'account/login.html'}),

)
