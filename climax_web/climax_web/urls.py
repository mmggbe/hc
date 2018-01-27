"""climax_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from alarm import views as al_views
from accounts import views as account_views

from django.contrib.auth import views
from mylogin.forms import LoginForm
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', al_views.index, name='home'),
    url(r'^admin/', include(admin.site.urls)),
 #   url(r'', include('mylogin.urls')), 
    url(r'', include('accounts.urls')),
#    url(r'^signup/$', account_views.signup, name='signup'),
#    url(r'^login/$', views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
#    url(r'^logout/$', views.logout, {'next_page': '/login'}),  
    url(r'^camera/', include ('camera.urls')),
    url(r'^history/', include ('history.urls')),
    url(r'^alarm/', include ('alarm.urls')),
    url(r'^horusadmin/', include ('horusadmin.urls')),
#    url(r'^$', index, name='index'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
