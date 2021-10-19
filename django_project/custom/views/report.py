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
            for dataset in category.datasetfile_set.all():
                if dataset.geonode_layer:
                    context['all_layer_ids'].append(dataset.geonode_layer.id)

        if self.request.GET.get('subRegion', None):
            context['subRegion'] = self.request.GET.get('subRegion').split(':')
        return context


def generate_report_pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    p.setPageSize((1200, 800))

    # Draw png template
    image_path = '/home/web/django_project/custom/static/report/report_template_1.png'
    p.drawImage(image_path, 0, 0, width=1200, height=800,
                     preserveAspectRatio=True)

    # p.setFillColorRGB(0.121, 0.247, 0.447)
    # p.rect(0, 0, 1200, 800, fill=1)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica", 70)
    p.drawString(50, 480, "Clean Cooking")
    p.drawString(50, 400, "Explorer")

    p.setFillColorRGB(0.470, 0.714, 0.824)
    p.setFont("Helvetica", 30)
    p.drawString(50, 340, "Regional Report for Nepal")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='Report.pdf')
