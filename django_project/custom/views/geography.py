from django.views.generic import TemplateView

from custom.models import Geography


class GeographyView(TemplateView):
    template_name = 'geography.html'

    def get_context_data(self, **kwargs):
        context = super(GeographyView, self).get_context_data(**kwargs)
        all_geo = Geography.objects.all()
        context['geography'] = []
        for geo in all_geo:
            download_links = geo.vector_boundary_layer.download_links()
            _geo = {
                'id': geo.id,
                'name': geo.name,
                'province_selector': geo.province_selector,
                'district_selector': geo.district_selector,
                'municipal_selector': geo.municipal_selector
            }
            for download_link in download_links:
                if 'GeoJSON' in str(download_link):
                    _geo['download_link'] = download_link[3]
            context['geography'].append(_geo)
        return context
