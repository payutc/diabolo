from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
v1_api = Api(api_name='v1')
from diabolo.api import api
import inspect

for name,obj in inspect.getmembers(api):
	if 'Resource' in name and 'ModelResource' != name and inspect.isclass(obj):
		v1_api.register(obj())

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'payutc.views.home', name='home'),
	# url(r'^payutc/', include('payutc.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include(v1_api.urls)),
)
