from django.conf.urls import url
from . import views

urlpatterns= [
        url(r'^$', views.index, name='index'),
        url(r'^cameraAdd/', views.cameraAdd),
        url(r'^cameraSettings/', views.cameraSettings),
        url(r'^saveCamera/', views.saveCamera),
        url(r'^cameraDelete/(?P<pk>\d+)$', views.cameraDelete, name='cameraDelete'),
        url(r'^cameraEdit/(?P<pk>\d+)$', views.cameraEdit, name='cameraEdit'),
        url(r'^cameraArming/', views.cameraArming, name='cameraArming'),
        url(r'^video/(?P<filename>[0-9a-zA-Z.]+)/$', views.video),
        
]
