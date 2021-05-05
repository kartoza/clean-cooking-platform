from geonode.urls import *
from filebrowser.sites import site

urlpatterns = [
                  url(r'^', include('custom.urls')),
                  url(r'^admin/filebrowser/', site.urls),
              ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
