from geonode.urls import *

urlpatterns = [
                  url(r'^', include('custom.urls')),
              ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
