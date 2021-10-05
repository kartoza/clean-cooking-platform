from django.views.generic import TemplateView

from custom.models import Geography
from custom.models.use_case import UseCase


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
        context['presets'] = context['use_case'].presets.all()
        if self.request.GET.get('subRegion', None):
            context['subRegion'] = self.request.GET.get('subRegion').split(':')
        return context
