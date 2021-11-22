import io
import textwrap

from django.views.generic import View
from django.http import FileResponse

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Table, PageBreak, TableStyle, Paragraph
)
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from core.settings.utils import absolute_path
from custom.models import Geography, UseCase, Preset, SummaryReportCategory, SummaryReportResult
from custom.views.summary_report import sample_raster_with_vector


class ReportPDFView(View):

    image_path = absolute_path(
        'custom', 'static', 'report', 'report_template_1.png')
    cca_logo_path = absolute_path(
        'custom', 'static', 'img', 'cca_logo_transparent.png'
    )
    demand_legend_path = absolute_path(
        'custom', 'static', 'img', 'demand_legend.png'
    )
    supply_legend_path = absolute_path(
        'custom', 'static', 'img', 'supply_legend.png'
    )
    page_width = 2000
    page_height = 1125
    sidebar_width = 700
    sidebar_x = page_width - sidebar_width
    sidebar_x_padding = 50
    navbar_height = 50
    geography = None
    summary_categories = None
    demand_tiff_file = None
    supply_tiff_file = None
    subregion = ''
    map_image = ''
    demand_image = None
    supply_image = None
    use_case = None
    preset = None
    demand_summary = []
    supply_summary = []
    total_population = 'X'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pdfmetrics.registerFont(
            TTFont('AktivGroteskCorpMedium',
                   absolute_path(
                       'custom',
                       'static/fonts/AktivGroteskCorp-Medium.ttf')))
        pdfmetrics.registerFont(
            TTFont('AktivGroteskCorpBold',
                   absolute_path(
                       'custom',
                       'static/fonts/AktivGroteskCorp-Bold.ttf')))
        pdfmetrics.registerFont(
            TTFont('AktivGroteskCorpLight',
                   absolute_path(
                       'custom',
                       'static/fonts/AktivGroteskCorp-Light.ttf')))
        registerFontFamily(
            'AktivGroteskCorp',
            normal='AktivGroteskCorpMedium',
            bold='AktivGroteskCorpBold',
            italic='AktivGroteskCorpLight')

    def _draw_wrapped_line(self, canvas, text, length, x_pos, y_pos, y_offset):
        """
        :param canvas: reportlab canvas
        :param text: the raw text to wrap
        :param length: the max number of characters per line
        :param x_pos: starting x position
        :param y_pos: starting y position
        :param y_offset: the amount of space to leave between wrapped lines
        """
        if len(text) > length:
            wraps = textwrap.wrap(text, length)
            for x in range(len(wraps)):
                canvas.drawString(x_pos, y_pos, wraps[x])
                y_pos -= y_offset
            y_pos += y_offset  # add back offset after last wrapped line
        else:
            canvas.drawString(x_pos, y_pos, text)
        return y_pos

    def _draw_footer(self, page, page_number = 1):

        page.setFillColorRGB(0.121, 0.247, 0.447)
        page.rect(0, 0, self.page_width, self.navbar_height,
                  stroke=0, fill=1)

        page.setFillColorRGB(0.459, 0.714, 0.831)
        page.setFont("AktivGroteskCorpLight", 25)
        page.drawString(self.page_width - 420,
                        self.navbar_height - 35,
                        "CLEAN COOKING ALLIANCE  —  {}".format(
                            page_number
                        ))

    def _draw_sidebar(self, page, color = (0.349, 0.549, 0.286)):

        page.setFillColorRGB(*color)
        page.rect(self.sidebar_x,
                  0, self.sidebar_width, self.page_height, stroke=0, fill=1)
        page.drawImage(self.cca_logo_path,
                       self.sidebar_x - 180, -250,
                       width=600,
                       preserveAspectRatio=True,
                       mask='auto')

    def _draw_title(self, page, title, sub_title):
        # Add title
        page.setFillColorRGB(29 / 255, 63 / 255, 116 / 255)
        page.setFont("AktivGroteskCorpMedium", 40)
        page.drawString(
            75, self.page_height - 100, title)
        page.setFont("AktivGroteskCorpBold", 50)
        page.drawString(
            75, self.page_height - 150, sub_title)
        page.setLineWidth(inch * 0.08)

        page.setStrokeColorRGB(29 / 255, 63 / 255, 116 / 255)
        page.line(
            75,
            self.page_height - 165,
            self.sidebar_x - 100,
            self.page_height - 165
        )

    def _draw_map(self, page, map_image, legend_path = None, img_width = 650):
        img = ImageReader(map_image)
        page.drawImage(
            img, (self.sidebar_x / 2) - (img_width / 2), 0,
            width=img_width,
            height=self.page_height,
            preserveAspectRatio=True,
            mask='auto')

        if legend_path:
            page.drawImage(
                legend_path,
                self.sidebar_x - 120, 100,
                width=100,
                preserveAspectRatio=True,
                mask='auto')

    def _draw_summary(self, page, summary_data):

        y_pos = self.page_height - 250
        x_pos = self.sidebar_x + 50
        page.setFillColorRGB(1, 1, 1)
        page.setStrokeColorRGB(1, 1, 1)
        page.setLineWidth(inch * 0.04)
        page.line(
            x_pos,
            y_pos,
            self.page_width - 50,
            y_pos
        )
        y_pos -= 50
        for summary in summary_data:
            page.setFont("AktivGroteskCorpLight", 30)
            prev_y_pos = y_pos
            y_pos = self._draw_wrapped_line(
                page,
                summary['desc'],
                25,
                x_pos + 300,
                y_pos,
                35
            )
            page.setFont("AktivGroteskCorpBold", 70)
            page.drawRightString(
                x_pos + 250,
                prev_y_pos - ((prev_y_pos-y_pos)/2) - 10,
                summary['value'])
            y_pos -= 30
            page.line(
                x_pos,
                y_pos,
                self.page_width - 50,
                y_pos
            )
            y_pos -= 50

    def draw_page_one(self, page):
        page.drawImage(self.image_path, 0, 0,
                    width=self.page_width,
                    height=self.page_height,
                    preserveAspectRatio=True)
        page.setFillColorRGB(1, 1, 1)
        page.setFont("AktivGroteskCorpBold", 110)
        page.drawString(50, 600, "Clean Cooking")
        page.drawString(50, 500, "Explorer")

        page.setFillColorRGB(0.470, 0.714, 0.824)
        page.setFont("AktivGroteskCorpMedium", 60)
        if self.geography:
            page.drawString(50, 420, "Regional Report for {}, {}".format(
                self.subregion,
                self.geography.name
            ))
        page.showPage()


    def draw_page_two(self, page):

        self._draw_sidebar(page)
        self._draw_footer(page, 2)
        self._draw_map(page, self.map_image, None, 900)
        self._draw_title(page, 'Regional Summary', self.subregion)

        # Add sidebar title
        page.setFillColorRGB(1, 1, 1)
        page.setFont("AktivGroteskCorpBold", 65)
        page.drawString(
            self.sidebar_x + self.sidebar_x_padding,
            self.page_height - 100, "Snapshot")

        page.setLineWidth(inch * 0.1)
        page.setStrokeColorRGB(1, 1, 1)
        page.line(
            self.sidebar_x + self.sidebar_x_padding,
            self.page_height - 130,
            self.page_width - self.sidebar_x_padding,
            self.page_height - 130
        )

        # Draw description
        page.setFillColorRGB(1, 1, 1)
        page.setFont("AktivGroteskCorpLight", 30)

        y_pos = self._draw_wrapped_line(
            page,
            self.preset.description,
            45,
            self.sidebar_x + self.sidebar_x_padding,
            self.page_height - 190,
            35
        )

        table_data = [
            ['', self.subregion],
            ['Population', self.total_population],
            ['Households', 'X'],
            ['Urban ratio', 'X%']
        ]

        table_width = self.sidebar_width
        table_height = 1000
        table_x = self.sidebar_x + self.sidebar_x_padding
        table_y = y_pos - 300

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (1, -1), colors.Color(
                red=29/255,green=63/255,blue=116/255)),
            ('FONTSIZE', (0, 0), (1, -1), 33),
            ('RIGHTPADDING', (0, 0), (1, -1), 50),
            ('LEFTPADDING', (0, 0), (1, -1), 50),
            ('BOTTOMPADDING', (0, 0), (1, -1), 30),
            ('ALIGN', (1, 1), (1, -1), "RIGHT"),
        ]))
        table.wrapOn(page, table_width, table_height)
        table.drawOn(page, table_x, table_y)

        page.showPage()

    def draw_page_three(self, page):
        if not self.demand_image:
            return

        for summary_category in self.summary_categories:
            summary_result, _ = SummaryReportResult.objects.get_or_create(
                summary_report_category=summary_category,
                category='demand'
            )
            summary_result.raster_file = self.demand_tiff_file
            summary_result.save()
            summary_result_data = sample_raster_with_vector(
                summary_result
            )
            self.demand_summary.append({
                'desc': 'Number of {} within areas of high demand index'.format(
                    summary_category.name
                ),
                'value': '{}'.format(summary_result_data['total_high'])
            })

        self._draw_sidebar(page, (0.459, 0.714, 0.831))
        self._draw_footer(page, 3)
        self._draw_title(page, 'Analysis', 'Demand index')
        self._draw_map(page, self.demand_image, self.demand_legend_path)
        self._draw_summary(page, self.demand_summary)

        page.setFillColorRGB(0, 0, 0)
        page.setFont("AktivGroteskCorpLight", 25)
        self._draw_wrapped_line(
            page,
            'This index helps us understand where there is high demand in the '
            'form of population and public needs for clean cooking.',
            100,
            100, 125, 40
        )

        page.showPage()

    def draw_page_four(self, page):
        if not self.supply_image:
            return

        for summary_category in self.summary_categories:
            summary_result, _ = SummaryReportResult.objects.get_or_create(
                summary_report_category=summary_category,
                category='supply'
            )
            summary_result.raster_file = self.supply_tiff_file
            summary_result.save()
            summary_result_data = sample_raster_with_vector(
                summary_result
            )
            self.supply_summary.append({
                'desc': 'Number of {} close to supply'.format(
                    summary_category.name
                ),
                'value': '{}'.format(summary_result_data['total_high'])
            })

        self._draw_sidebar(page)
        self._draw_footer(page, 4)
        self._draw_title(page, 'Analysis', 'Supply index')
        self._draw_map(page, self.supply_image, self.supply_legend_path)
        self._draw_summary(page, self.supply_summary)

        page.setFillColorRGB(0, 0, 0)
        page.setFont("AktivGroteskCorpLight", 25)
        self._draw_wrapped_line(
            page,
            'This index helps us understand where there is high '
            'potential for electric cooking.',
            100,
            75, 125, 40
        )

        page.showPage()

    def post(self, request, *args, **kwargs):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        geo_id = request.POST.get('geoId', '')
        use_case_id = request.POST.get('useCaseId', None)
        preset_id = request.POST.get('scenarioId', None)

        self.map_image = request.POST.get('mapImage', '')
        self.demand_image = request.POST.get('demandImage', None)
        self.demand_tiff_file = request.FILES.get('demandTiff', None)
        self.supply_tiff_file = request.FILES.get('supplyTiff', None)
        self.supply_image = request.POST.get('supplyImage', None)
        self.subregion = request.POST.get('subRegion', '')
        self.demand_high_percentage = (
            request.POST.get('demandDataHighPercentage', '')
        )
        self.supply_high_percentage = (
            request.POST.get('supplyDataHighPercentage', '')
        )

        self.total_population = (
            request.POST.get('totalPopulation', '')
        )
        self.geography = Geography.objects.get(id=geo_id)

        self.summary_categories = SummaryReportCategory.objects.filter(
            preset_id=preset_id
        )

        self.demand_summary = [
            {
                'desc': 'Population within areas of high demand index',
                'value': f'{self.demand_high_percentage}%'
            }
        ]

        self.supply_summary = [
            {
                'desc': 'Population within areas of high supply index',
                'value': f'{self.supply_high_percentage}%'
            }
        ]

        if use_case_id:
            try:
                self.use_case = UseCase.objects.get(id=use_case_id)
            except UseCase.DoesNotExist:
                pass

        if preset_id:
            try:
                self.preset = Preset.objects.get(id=preset_id)
            except Preset.DoesNotExist:
                pass

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)
        p.setPageSize((self.page_width, self.page_height))

        self.draw_page_one(p)
        PageBreak()
        self.draw_page_two(p)
        PageBreak()
        self.draw_page_three(p)
        PageBreak()
        self.draw_page_four(p)
        PageBreak()

        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Report.pdf')
