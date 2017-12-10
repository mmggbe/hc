from django.conf.urls import url
from . import views

urlpatterns= [
        url(r'^$', views.cameraList, name='cameraList'),
        url(r'^cameraAdd/', views.cameraAdd),
        url(r'^cameraEdit/(?P<pk>\d+)$', views.cameraEdit, name='cameraEdit'),
        url(r'^cameraSettings/', views.cameraSettings),
        url(r'^saveCamera/', views.saveCamera),
        url(r'^cameraDelete/(?P<pk>\d+)$', views.cameraDelete, name='cameraDelete'),
        url(r'^cameraTest/(?P<pk>\d+)$', views.cameraTest, name='cameraTest'),
        url(r'^cameraRT/(?P<pk>\d+)$', views.cameraRT, name='cameraRT'),
        url(r'^cameraRTStop/(?P<pk>\d+)$', views.cameraRTStop, name='cameraRTStop'),
        url(r'^saveAction/', views.saveAction),
        url(r'^cameraArming/', views.cameraArming, name='cameraArming'),
        url(r'^video/(?P<filename>[0-9a-zA-Z.]+)/$', views.video),
        
]
