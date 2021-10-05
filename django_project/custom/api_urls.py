from django.conf.urls import url
from custom.api_views import (
    BoundariesDataset,
    GeographyDetail,
    GeographyList,
    DatasetDetail,
    DatasetList
)
from custom.api_views.subregion import SubregionListAPI

urlpatterns = [
    url(r'^geography/$',
        GeographyDetail.as_view()),
    url(r'^geography-list/$',
        GeographyList.as_view()),
    url(r'^dataset/$',
        DatasetDetail.as_view()),
    url(r'^datasets/$',
        DatasetList.as_view()),
    url(r'^boundaries-dataset/$',
        BoundariesDataset.as_view()),
    url(r'^subregion-list/(?P<geo_id>\d+)/(?P<subregion_selector>.*)/$',
        SubregionListAPI.as_view())
]
