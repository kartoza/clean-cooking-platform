from django.conf import settings
from django.views.generic import TemplateView

from custom.models import Geography, UseCase, Preset


class ToolView(TemplateView):
    template_name = 'eae/tool.html'
    context_object_name = 'tool'

    def get(self, request, *args):
        geo = request.GET.get('geo', None)
        filters = {}
        if geo:
            filters = {
                'id': geo
            }
        return super(ToolView, self).get(request, *args)

    def get_context_data(self, **kwargs):
        context = super(ToolView, self).get_context_data(**kwargs)
        context['MAPBOX_TOKEN'] = settings.MAPBOX_TOKEN
        context['MAPBOX_THEME'] = settings.MAPBOX_THEME
        context['geoserver_url'] = settings.GEOSERVER_PUBLIC_LOCATION
        context['analysis_type'] = []
        if self.request.GET.get('useCase'):
            try:
                context['use_case'] = UseCase.objects.get(
                    id=self.request.GET.get('useCase')
                )
            except UseCase.DoesNotExist:
                context['use_case'] = ''
        if self.request.GET.get('preset'):
            try:
                context['preset'] = Preset.objects.get(
                    id=self.request.GET.get('preset')
                )
                context['analysis_type'] = list(
                    context['preset'].summaryreportcategory_set.all(
                    ).values_list('analysis', flat=True)
                )
            except Preset.DoesNotExist:
                context['preset'] = ''
        geo = Geography.objects.filter(
            online=True
        )
        if geo.exists():
            context['GEO'] = geo[0]
        return context

