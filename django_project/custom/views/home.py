from django.http import Http404
from django.views.generic import ListView, TemplateView
from geonode.maps.views import map_view

from custom.models.map_slug import MapSlugMapping


class HomeView(ListView):
    model = MapSlugMapping
    paginate_by = 100
    template_name = 'eae/index.html'
    context_object_name = 'maps'


def map_view_with_slug(request, slug):
    try:
        map = MapSlugMapping.objects.get(slug=slug)
    except MapSlugMapping.DoesNotExist:
        raise Http404("Map does not exist")

    return map_view(request, mapid=map.map.id)
