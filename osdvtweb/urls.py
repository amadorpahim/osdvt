from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    #(r'^osdvtweb/(?P<mac>\d+)/$', 'osdvtweb.vmadmin.views.index'),
    (r'^rest/', include('osdvtweb.osdvtadmin.urls')),
    #(r'^osdvtweb/(?P<mac>([a-fA-F0-9]{2}[:|\-]?){6})/', 'osdvtweb.osdvtadmin.views.index'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),



)
