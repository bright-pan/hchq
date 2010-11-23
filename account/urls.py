from django.conf.urls.defaults import *

urlpatterns = patterns('hchq.account.views',
                        
      (r'^account/login$', 'login', {'template_name' : 'account/login.html'}),
#      (r'^account/logout$', logout, {'template_name' : 'account/logout.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
#      (r'^account/login$', login, {'template_name' : 'account/login.html'}),
                        
)
