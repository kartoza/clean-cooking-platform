from django.views.generic import TemplateView

from custom.models import UseCase


class UseCaseView(TemplateView):
    template_name = 'use_case.html'

    def get_context_data(self, **kwargs):
        context = super(UseCaseView, self).get_context_data(**kwargs)
        context['use_cases'] = UseCase.objects.all()
        return context
