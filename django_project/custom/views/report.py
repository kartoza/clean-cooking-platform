import io

from django.conf import settings
from django.views.generic import TemplateView
from django.http import FileResponse

from reportlab.pdfgen import canvas

from custom.models import Geography, Category
from custom.models.use_case import UseCase
from custom.serializers.preset_serializer import PresetSerializer


class ReportView(TemplateView):
    template_name = 'reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)

        context['geoserver_url'] = settings.GEOSERVER_PUBLIC_LOCATION
        context['use_case'] = UseCase.objects.get(
            id=self.request.GET.get('useCase')
        )
        context['geo'] = Geography.objects.get(
            id=self.request.GET.get('geoId')
        )
        context['presets'] = PresetSerializer(
            context['use_case'].presets.all(),
            many=True
        ).data
        context['MAPBOX_TOKEN'] = settings.MAPBOX_TOKEN
        context['MAPBOX_THEME'] = settings.MAPBOX_THEME
        context['all_layer_ids'] = []

        all_category = Category.objects.filter(
            geography__id=self.request.GET.get('geoId'),
            boundary_layer=False,
            online=True
        )
        for category in all_category:
            for dataset in category.datasetfile_set.filter(
                    geonode_layer__isnull=False):
                context['all_layer_ids'].append(dataset.geonode_layer.id)

        if self.request.GET.get('subRegion', None):
            context['subRegion'] = self.request.GET.get('subRegion').split(':')
        return context
