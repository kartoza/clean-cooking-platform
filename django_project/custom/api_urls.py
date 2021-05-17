from django.conf.urls import url
from custom.api_views import (
    GeographyDetail,
    GeographyList,
    DatasetDetail,
    DatasetList
)

urlpatterns = [
    url(r'^geography/$',
        GeographyDetail.as_view()),
    url(r'^geography-list/$',
        GeographyList.as_view()),
    url(r'^dataset/$',
        DatasetDetail.as_view()),
    url(r'^datasets/$',
        DatasetList.as_view()),
]
