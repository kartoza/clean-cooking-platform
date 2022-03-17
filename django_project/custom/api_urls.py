from django.conf.urls import url
from custom.api_views import (
    BoundariesDataset,
    GeographyDetail,
    GeographyList,
    DatasetDetail,
    DatasetList,
    GeographyRasterMask
)
from custom.api_views.household import CalculateReport
from custom.api_views.subregion import (
    SubregionListAPI,
    ClipLayerByRegion
)
from custom.api_views.style import StyleApiView
from custom.api_views.map_image import MapImageApiView

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
    url(r'^subregion-list/(?P<geo_id>\d+)/'
        r'(?P<subregion_selector>[a-zA-Z0-9 ]*)/$',
        SubregionListAPI.as_view()),
    url(r'^subregion-list/(?P<geo_id>\d+)/'
        r'(?P<subregion_selector>[a-zA-Z0-9_ ]*)/'
        r'(?P<subregion_value>[a-zA-Z0-9_ ]*)/$',
        SubregionListAPI.as_view()),
    url(r'^geography-raster-mask/$',
        GeographyRasterMask.as_view()),
    url(r'^clip-layer-by-region/$',
        ClipLayerByRegion.as_view()),
    url(r'^style-api/$',
        StyleApiView.as_view()),
    url(r'^map-image-api/$',
        MapImageApiView.as_view()),
    url(r'^calculate-report/$',
        CalculateReport.as_view())
]
