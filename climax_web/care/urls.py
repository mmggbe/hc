from django.conf.urls import url
from care import views

urlpatterns= [
    url(r'^$', views.carePage, name='care'),      
    url(r'^cmd$', views.care_cmd, name='careMode'), 
    url(r'^add_rule$', views.care_add_rule, name='careAddRule'),
    url(r'^del_rule(?P<pk>\d+)$', views.care_del_rule, name='careDelRule'),
]
