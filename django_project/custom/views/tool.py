from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView

from custom.models import Geography


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
        geo = Geography.objects.filter(
            online=True,
            **filters
        )
        if geo.count() != 1:
            return redirect('tool-select')
        return super(ToolView, self).get(request, *args)

    def get_context_data(self, **kwargs):
        context = super(ToolView, self).get_context_data(**kwargs)
        context['MAPBOX_TOKEN'] = settings.MAPBOX_TOKEN
        context['MAPBOX_THEME'] = settings.MAPBOX_THEME
        geo = Geography.objects.filter(
            online=True
        )
        if geo.exists():
            context['DEFAULT_GEO_ID'] = geo[0].id
        return context

