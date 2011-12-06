from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from osdvtweb.osdvtadmin.views import VM

urlpatterns = patterns('osdvtweb.osdvtadmin.views',
    # Example:
    # (r'^osdvtadmin/', include('osdvtadmin.foo.urls')),
    (r'vm/$', VM.as_view()),
    #(r'$', 'index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
