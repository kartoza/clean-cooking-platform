import io
import re
import base64

from django.views.generic import View
from django.http import FileResponse

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, PageBreak, TableStyle
from reportlab.lib.utils import ImageReader

from core.settings.utils import absolute_path
from custom.models import Geography


class ReportPDFView(View):

    image_path = absolute_path(
        'custom', 'static', 'report', 'report_template_1.png')
    page_width = 2000
    page_height = 1125
    geography = None
    subregion = ''
    map_image = 'data:image/png;base64'

    def decode_base64(self, data, altchars=b'+/'):
        """Decode base64, padding being optional.

        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.

        """
        data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
        missing_padding = len(data) % 4
        if missing_padding:
            data += b'=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)

    def draw_page_one(self, page):
        page.drawImage(self.image_path, 0, 0,
                    width=self.page_width,
                    height=self.page_height,
                    preserveAspectRatio=True)
        page.setFillColorRGB(1, 1, 1)
        page.setFont("Helvetica", 110)
        page.drawString(50, 600, "Clean Cooking")
        page.drawString(50, 500, "Explorer")

        page.setFillColorRGB(0.470, 0.714, 0.824)
        page.setFont("Helvetica", 60)
        if self.geography:
            page.drawString(50, 420, "Regional Report for {}, {}".format(
                self.subregion,
                self.geography.name
            ))
        page.showPage()

    def draw_page_two(self, page):
        sidebar_width = 700
        sidebar_x = self.page_width - sidebar_width
        navbar_height = 50
        img = ImageReader(self.map_image)
        img_width, img_height = img.getSize()
        page.drawImage(
            img, (sidebar_x / 2) - (img_width / 2), 0,
            width=img_width,
            height=self.page_height,
            preserveAspectRatio=True,
            mask='auto')
        page.setFillColorRGB(0.349, 0.549, 0.286)

        page.rect(sidebar_x,
                  0, sidebar_width, self.page_height, stroke=0, fill=1)

        page.setFillColorRGB(0.121, 0.247, 0.447)
        page.rect(0, 0, self.page_width, navbar_height,
                  stroke=0, fill=1)

        table_data = [
            ['', self.subregion],
            ['Population', 'X'],
            ['Households', 'X'],
            ['Urban ratio', 'X%']
        ]

        table_width = sidebar_width - 100
        table_height = 1000
        table_x = sidebar_x + 100
        table_y = self.page_height - 800


        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (1, -1), colors.Color(
                red=0.470,green=0.714,blue=0.824)),
            ('FONTSIZE', (0, 0), (1, -1), 33),
            ('RIGHTPADDING', (0, 0), (1, -1), 30),
            ('LEFTPADDING', (0, 0), (1, -1), 30),
            ('BOTTOMPADDING', (0, 0), (1, -1), 30),
            ('ALIGN', (1, 1), (1, -1), "RIGHT"),
        ]))
        table.wrapOn(page, table_width, table_height)
        table.drawOn(page, table_x, table_y)

        page.showPage()

    def post(self, request, *args, **kwargs):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        geo_id = request.POST.get('geoId', '')

        self.map_image = request.POST.get('mapImage', '')
        self.subregion = request.POST.get('subRegion', '')
        self.geography = Geography.objects.get(id=geo_id)

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)
        p.setPageSize((self.page_width, self.page_height))

        self.draw_page_one(p)
        PageBreak()
        self.draw_page_two(p)

        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Report.pdf')
