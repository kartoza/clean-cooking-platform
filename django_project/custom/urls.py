# coding=utf-8
"""Urls for custom apps."""

from django.conf.urls import url
from django.urls import include
from custom.views import HomeView, map_view_with_slug

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

wagtail = [
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^pages/', include(wagtail_urls)),
]

urlpatterns = [
    url(r'^$',
        view=HomeView.as_view(),
        name='home'),
    url(r'^view/(?P<slug>[^/]+)$',
        view=map_view_with_slug,
        name='map_view_slug'),
    url('wagtail/', include(wagtail)),
]
