from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^home/', views.apihome, name='api_home'),
    url(r'^report', views.report),
    url(r'^$', views.apihome, name='api_home'),
    url(r'^project(?P<projectId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/$', views.apilist, name="api_list"),
    url(r'^project(?P<projectId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/api(?P<apiId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/doc/$', views.api_doc, name="api_doc"),
    url(r'^project(?P<projectId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/api(?P<apiId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/debug/$', views.api_debug, name="api_debug"),
    url(r'^project(?P<projectId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/api(?P<apiId>[a-z,A-Z,{,},.,0-9,:,%,-]+)/test/$', views.api_test, name="api_test"),
]
