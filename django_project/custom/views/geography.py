from django.views.generic import TemplateView

from custom.models import Geography


class GeographyView(TemplateView):
    template_name = 'geography.html'

    def get_context_data(self, **kwargs):
        context = super(GeographyView, self).get_context_data(**kwargs)
        context['geography'] = Geography.objects.all()
        return context
