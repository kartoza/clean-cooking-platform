from django.conf.urls import url
from custom.api_views import (
    BoundariesDataset,
    GeographyDetail,
    GeographyList,
    DatasetDetail,
    DatasetList,
    GeographyRasterMask
)
from custom.api_views.household import CalculateHousehold
from custom.api_views.subregion import (
    SubregionListAPI,
    ClipLayerByRegion
)
from custom.api_views.style import StyleApiView

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
        SubregionListAPI.as_view()),
    url(r'^geography-raster-mask/$',
        GeographyRasterMask.as_view()),
    url(r'^clip-layer-by-region/$',
        ClipLayerByRegion.as_view()),
    url(r'^style-api/$',
        StyleApiView.as_view()),
    url(r'^calculate-household/$',
        CalculateHousehold.as_view())
]
