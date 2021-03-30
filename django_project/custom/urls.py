# coding=utf-8
"""Urls for custom apps."""

from django.conf.urls import url
from django.urls import include
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
    url(r'^view/(?P<slug>[^/]+)$',
        view=map_view_with_slug,
        name='map_view_slug'),
]
