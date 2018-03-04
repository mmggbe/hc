from django.conf.urls import url
from alarm import views

urlpatterns= [

        url(r'^userslist$', views.users_list, name='users_list'),
        
        url(r'^userslist/(?P<pk>\d+)/edit/$', views.user_edit, name='user_edit'),
        
        url(r'^sensorslist$', views.sensors_list, name='sensors_list'),

        url(r'^sensordelete/(?P<pk>\d+)$', views.sensor_delete, name='sensor_delete'), 
        url(r'^sensormodify/(?P<pk>\d+)$', views.sensor_modify, name='sensor_modify'), 

        url(r'^gateway/new$', views.gateway_new, name='gateway_new'),
        url(r'^gateway/list$', views.gateways_list, name='gateways_list'), 
        url(r'^gateway/delete/(?P<pk>\d+)$', views.gateways_delete, name='gateway_delete'),
      
        url(r'^gateway/status$', views.gateway_status, name='gateway_status'),                                                                                   
        url(r'^gateway/smartplug$', views.smartplug_list, name='smartplug_list'),
        url(r'^gateway/smartplug/cmd$', views.smartplug_cmd, name='smartplug_cmd'),
        
        url(r'^contact$',views.HC_contact_edit, name='HC_contact'),

]
