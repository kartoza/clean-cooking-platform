from django.conf.urls import url
from custom.api_views import (
    GeographyDetail,
    DatasetDetail,
    DatasetList
)

urlpatterns = [
    url(r'^geography/$',
        GeographyDetail.as_view()),
    url(r'^dataset/$',
        DatasetDetail.as_view()),
    url(r'^datasets/$',
        DatasetList.as_view()),
]
