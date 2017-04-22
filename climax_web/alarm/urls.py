from django.conf.urls import url
from . import views

urlpatterns= [
        url(r'^$', views.index, name='index'),
        url(r'^userslist$', views.users_list, name='users_list'),
#        url(r'^userslist/(?P<pk>\d+)$', views.user_details, name='user_details'),
        
        url(r'^userslist/(?P<pk>\d+)/edit/$', views.user_edit, name='user_edit'),
        
        url(r'^sensorslist$', views.sensors_list, name='sensors_list'),
#        url(r'^sensorslist/(?P<pk>\d+)$', views.sensor_details, name='sensor_details'), 
        url(r'^sensordelete/(?P<pk>\d+)$', views.sensor_delete, name='sensor_delete'), 
        url(r'^sensormodify/(?P<pk>\d+)$', views.sensor_modify, name='sensor_modify'), 
#        url(r'^sensormodify/sensormodified$', views.sensors_list, name='sensormodified'), 

        url(r'^gateway/new$', views.gateway_new, name='gateway_new'),
        url(r'^gateway/list$', views.gateways_list, name='gateways_list'), 
        url(r'^gateway/delete/(?P<pk>\d+)$', views.gateways_delete, name='gateway_delete'),
      
        url(r'^gateway/status$', views.gateway_status, name='gateway_status'),                                                                                   
        url(r'^gateway/smartplug$', views.smartplug_list, name='smartplug_list'),

]
