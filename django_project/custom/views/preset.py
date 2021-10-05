from django.views.generic import TemplateView

from custom.models.preset import Preset


class PresetView(TemplateView):
    template_name = 'preset.html'

    def get_context_data(self, **kwargs):
        context = super(PresetView, self).get_context_data(**kwargs)
        context['presets'] = Preset.objects.all()
        return context
