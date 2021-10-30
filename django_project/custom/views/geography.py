from django.views.generic import TemplateView
from django.conf import settings

from custom.models import Geography


class GeographyView(TemplateView):
    template_name = 'geography.html'

    def get_context_data(self, **kwargs):
        context = super(GeographyView, self).get_context_data(**kwargs)
        all_geo = Geography.objects.all()
        context['geography'] = []
        context['geoserver_url'] = settings.GEOSERVER_PUBLIC_LOCATION
        context['MAPBOX_TOKEN'] = settings.MAPBOX_TOKEN
        context['MAPBOX_THEME'] = settings.MAPBOX_THEME
        for geo in all_geo:
            download_links = geo.vector_boundary_layer.download_links()
            _geo = {
                'id': geo.id,
                'name': geo.name,
                'layer_name': str(geo.vector_boundary_layer),
                'province_selector': geo.province_selector,
                'district_selector': geo.district_selector,
                'municipal_selector': geo.municipal_selector,
                'bbox': geo.vector_boundary_layer.bbox_string
            }
            for download_link in download_links:
                if 'GeoJSON' in str(download_link):
                    _geo['download_link'] = download_link[3]
            context['geography'].append(_geo)
        return context
