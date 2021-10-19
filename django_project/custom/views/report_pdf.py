import io

from django.views.generic import View
from django.http import FileResponse

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, PageBreak, TableStyle

from core.settings.utils import absolute_path


class ReportPDFView(View):

    image_path = absolute_path(
        'custom', 'static', 'report', 'report_template_1.png')
    page_width = 2000
    page_height = 1125

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
        page.drawString(50, 420, "Regional Report for Nepal")
        page.showPage()

    def draw_page_two(self, page):
        sidebar_width = 700
        sidebar_x = self.page_width - sidebar_width
        navbar_height = 50

        page.setFillColorRGB(0.349, 0.549, 0.286)


        page.rect(sidebar_x,
                  0, sidebar_width, self.page_height, stroke=0, fill=1)

        page.setFillColorRGB(0.121, 0.247, 0.447)
        page.rect(0, 0, self.page_width, navbar_height,
                  stroke=0, fill=1)

        table_data = [
            ['', 'Region name'],
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

    def get(self, request, *args, **kwargs):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

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
