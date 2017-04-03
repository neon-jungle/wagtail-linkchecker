from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from wagtaillinkchecker import views

urlpatterns = [
    url(r'^$', views.index,
        name='wagtaillinkchecker'),
    url(r'^settings/$', views.settings,
        name='wagtaillinkchecker_settings'),
    url(r'^scan/$', views.run_scan,
        name='wagtaillinkchecker_runscan'),
    url(r'^scan/(?P<scan_pk>\d+)/$', views.scan,
        name='wagtaillinkchecker_scan'),
    url(r'^scan/(?P<scan_pk>\d+)/delete$', views.delete,
        name='wagtaillinkchecker_delete'),
]
