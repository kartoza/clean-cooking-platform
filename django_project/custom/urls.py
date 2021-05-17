# coding=utf-8
"""Urls for custom apps."""

from django.conf.urls import url
from django.urls import include
from django.views.generic import TemplateView
from custom.proxy import proxy_request
from custom.views import HomeView, map_view_with_slug, ToolView

urlpatterns = [
    url(r'^$',
        view=HomeView.as_view(),
        name='home'),
    url(r'^api/',
        include('custom.api_urls')),
    url(r'^tool/$',
        view=ToolView.as_view(),
        name='tool'),
    url(r'^tool/select/$',
        view=TemplateView.as_view(template_name='eae/select-geo.html'),
        name='tool-select'),
    url('proxy_cca/(?P<path>.*)', proxy_request),
    url(r'^methodology/$',
        view=TemplateView.as_view(template_name='eae/methodology.html'),
        name='methodology'),
    url(r'^about-us/$',
        view=TemplateView.as_view(template_name='eae/about.html'),
        name='about'),
    url(r'^user-stories/$',
        view=TemplateView.as_view(template_name='eae/user-stories.html'),
        name='user-stories'),
    url(r'^sample-analysis/$',
        view=TemplateView.as_view(template_name='eae/sample-analysis.html'),
        name='sample-analysis'),
    url(r'^view/(?P<slug>[^/]+)$',
        view=map_view_with_slug,
        name='map_view_slug'),
]
