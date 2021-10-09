from django.conf import settings
from django.views.generic import TemplateView

from custom.models import Geography
from custom.models.use_case import UseCase
from custom.serializers.preset_serializer import PresetSerializer


class ReportView(TemplateView):
    template_name = 'reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
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

        if self.request.GET.get('subRegion', None):
            context['subRegion'] = self.request.GET.get('subRegion').split(':')
        return context
