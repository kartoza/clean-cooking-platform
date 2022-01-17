from django.views.generic import TemplateView

from custom.models import UseCase, Geography


class UseCaseView(TemplateView):
    template_name = 'use_case.html'

    def get_context_data(self, **kwargs):
        context = super(UseCaseView, self).get_context_data(**kwargs)
        context['use_cases'] = UseCase.objects.filter(
            geography=self.request.GET.get('geoId')
        )
        context['geo'] = Geography.objects.get(
            id=self.request.GET.get('geoId')
        )
        if self.request.GET.get('subRegion', None):
            context['subRegion'] = self.request.GET.get('subRegion').split(':')
        return context
