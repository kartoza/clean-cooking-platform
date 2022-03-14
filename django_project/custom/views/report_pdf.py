import io
import math
import os.path
import textwrap
from datetime import datetime

from urllib.parse import urlparse
from urllib.parse import parse_qs

import requests
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, PageBreak, TableStyle, Paragraph
)
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from core.settings.utils import absolute_path
from custom.models import (
    Geography, UseCase, Preset,
    SummaryReportCategory, SummaryReportResult, SummaryReportDataset, MapImage
)
from custom.tools.report_calculation import (
    calculate_household, calculate_urban, calculate_cooking_with_traditional,
    calculate_poverty, calculate_poverty_supply_layer_distance
)
from custom.tools.category import category_from_url
from custom.views.summary_report import sample_raster_with_vector


@method_decorator(csrf_exempt, name='dispatch')
class ReportPDFView(View):

    image_path = absolute_path(
        'custom', 'static', 'report', 'report_template_1.png')
    image_path_end = absolute_path(
        'custom', 'static', 'report', 'report_template_end.png')
    cca_logo_path = absolute_path(
        'custom', 'static', 'img', 'cca_logo_transparent.png'
    )
    demand_legend_path = absolute_path(
        'custom', 'static', 'img', 'demand_legend.png'
    )
    ccp_legend_path = absolute_path(
        'custom', 'static', 'img', 'ccp_legend.png'
    )
    supply_legend_path = absolute_path(
        'custom', 'static', 'img', 'supply_legend.png'
    )
    ani_legend_path = absolute_path(
        'custom', 'static', 'img', 'ani_legend.png'
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
    ani_tiff_file = None
    ccp_tiff_file = None
    subregion = ''
    map_image = ''
    demand_image = None
    ccp_image = None
    supply_image = None
    ani_image = None
    use_case = None
    preset = None
    demand_summary = []
    supply_summary = []
    ani_summary = []
    table_summary_data = []
    total_population = 0
    total_urban_population = 0
    total_household = 0
    total_cooking_percentage = 0
    total_poverty = 0
    boundary = ''
    categories = []
    table_supply_demand_y_pos = 0

    default_font = 'AktivGroteskCorpMedium'
    default_font_bold = 'AktivGroteskCorpBold'
    default_font_light = 'AktivGroteskCorpLight'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pdfmetrics.registerFont(
            TTFont(self.default_font,
                   absolute_path(
                       'custom',
                       'static/fonts/AktivGroteskCorp-Medium.ttf')))
        pdfmetrics.registerFont(
            TTFont(self.default_font_bold,
                   absolute_path(
                       'custom',
                       'static/fonts/AktivGroteskCorp-Bold.ttf')))
        pdfmetrics.registerFont(
            TTFont(self.default_font_light,
                   absolute_path(
                       'custom',
                       'static/fonts/AktivGroteskCorp-Light.ttf')))
        registerFontFamily(
            'AktivGroteskCorp',
            normal=self.default_font,
            bold=self.default_font_bold,
            italic=self.default_font_light)

    def _draw_supply_demand_table(self, canvas, y_pos):
        data = {
            'demand': [],
            'supply': [],
            'other': []
        }

        population_added = False
        table_y = y_pos - 30

        for category in self.categories:
            if 'population' in category.name_long.lower():
                population_added = True
            if category.demand_index:
                data['demand'].append(category.name_long)
            if category.supply_index:
                data['supply'].append(category.name_long)
            if not category.demand_index and not category.supply_index:
                data['other'].append(category.name_long)

        if not population_added:
            data['other'].append('Population')

        table_data = [
            ['Supply', 'Demand', 'Other'],
        ]

        for supply in data['supply']:
            table_data.append([supply, '', ''])

        demand_index = 1
        for demand in data['demand']:
            if len(table_data) > demand_index:
                table_data[demand_index][1] = demand
            else:
                table_data.append(['', demand, ''])
            demand_index += 1

        other_index = 1
        if 'other' in data:
            for other in data['other']:
                if len(table_data) > other_index:
                    table_data[other_index][2] = other
                else:
                    table_data.append(['', '', other])
                other_index += 1

        table_width = 2000
        table_height = 200
        table_x = 75

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (2, 0), self.default_font_bold),
            ('BACKGROUND', (0, 0), (2, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (2, -1), colors.Color(
                red=29 / 255, green=63 / 255, blue=116 / 255)),
            ('FONTSIZE', (0, 0), (2, -1), 23),
            ('RIGHTPADDING', (0, 0), (2, -1), 50),
            ('LEFTPADDING', (0, 0), (2, -1), 20),
            ('BOTTOMPADDING', (0, 0), (2, -1), 30),
        ]

        table_y -= len(table_data) * 45

        table = Table(table_data, colWidths=[4*inch,4*inch])
        table.setStyle(TableStyle(table_style))
        table.wrapOn(canvas, table_width, table_height)
        table.drawOn(canvas, table_x, table_y)
        self.table_supply_demand_y_pos = table_y

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
        page.setFont(self.default_font, 25)
        page.drawString(self.page_width - 420,
                        self.navbar_height - 35,
                        "CLEAN COOKING ALLIANCE - {}".format(
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

    def _draw_title(self,
                    page,
                    title,
                    sub_title,
                    sidebar_exists = True,
                    color = (29 / 255, 63 / 255, 116 / 255)):
        # Add title
        page.setFillColorRGB(*color)
        title_height = 0
        if title:
            title_height = 50
            page.setFont(self.default_font, 40)
            page.drawString(
                75, self.page_height - 100, title)
        page.setFont(self.default_font_bold, 50)
        page.drawString(
            75, self.page_height - (100 + title_height), sub_title)
        page.setLineWidth(inch * 0.08)

        page.setStrokeColorRGB(*color)
        page.line(
            75,
            self.page_height - (115 + title_height),
            self.sidebar_x - 100 if sidebar_exists else self.page_width - 100,
            self.page_height - (115 + title_height)
        )

    def _draw_map(self, page, map_image, legend_path = None, img_width = 650,
                  x = None, y = 0):
        img = ImageReader(map_image)
        x_pos = x if x else (self.sidebar_x / 4) - (img_width / 4)
        page.drawImage(
            img, x_pos, y,
            width=img_width,
            height=self.page_height,
            preserveAspectRatio=True,
            mask='auto')

        if legend_path:
            legend_x_pos = (x + img_width + 50) if x else self.sidebar_x - 170
            page.drawImage(
                legend_path,
                legend_x_pos,
                100,
                width=150,
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
            page.setFont(self.default_font_light, 30)
            prev_y_pos = y_pos
            y_pos = self._draw_wrapped_line(
                page,
                summary['desc'],
                20,
                x_pos + 300,
                y_pos,
                35
            )
            summary_value_length = len(str(summary['value']))
            if summary_value_length > 7:
                page.setFont(self.default_font_bold,
                             70 - (math.sqrt(summary_value_length - 7) * 12))
            else:
                page.setFont(self.default_font_bold, 70)
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

    def _calculate_demand_supply(self, raster_file, analysis):
        result = []
        boundary = self.boundary
        if not boundary:
            boundary = 'All'
        if raster_file:
            for summary_category in self.summary_categories.filter(
                analysis=analysis
            ):
                if not summary_category.vector_layer:
                    continue
                summary_result, _ = SummaryReportResult.objects.get_or_create(
                    summary_report_category=summary_category,
                    analysis=analysis,
                    boundary_uuid=boundary
                )
                dataset_file, created = (
                    SummaryReportDataset.get_or_create_dataset_file(
                        boundary,
                        raster_file
                    )
                )
                if summary_result.dataset_file != dataset_file:
                    summary_result.result = {}
                    summary_result.dataset_file = dataset_file
                    summary_result.save()

                summary_result_data = sample_raster_with_vector(
                    summary_result
                )
                summary_result_data['label'] = summary_category.name
                summary_result_data['category'] = summary_category.category
                result.append(summary_result_data)
        return result

    def _calculate_ani_data(self, ani_categories):
        result = []
        boundary = self.boundary
        for ani_category in ani_categories:
            summary_result_data = calculate_poverty_supply_layer_distance(
                self.geography, boundary, ani_category.supply_layer)
            summary_result_data['label'] = ani_category.name
            summary_result_data['category'] = ani_category.category
            result.append(summary_result_data)
        return result

    def draw_page_one(self, page):
        page.drawImage(self.image_path, 0, 0,
                    width=self.page_width,
                    height=self.page_height,
                    preserveAspectRatio=True)
        page.setFillColorRGB(1, 1, 1)
        page.setFont(self.default_font_bold, 110)
        page.drawString(50, 600, "Clean Cooking")
        page.drawString(50, 500, "Explorer")

        page.setFillColorRGB(0.470, 0.714, 0.824)
        page.setFont(self.default_font, 60)
        if self.geography:
            page.drawString(50, 420, "Regional Report for {}, {}".format(
                self.subregion,
                self.geography.name
            ))

        page.drawString(50, 330, str(datetime.now().date()))
        page.showPage()

    def draw_page_end(self, page):
        page.drawImage(self.image_path_end, 0, 0,
                    width=self.page_width,
                    height=self.page_height,
                    preserveAspectRatio=True)
        page.setFillColorRGB(1, 1, 1)
        style = ParagraphStyle(
            name=self.default_font,
            fontName=self.default_font,
            fontSize=25,
            textColor=colors.white,
            alignment=TA_LEFT,
        )
        p = Paragraph(
            "The Clean Cooking Explorer adheres to the data quality standards <br/><br/><br/>"
            "set in place by WRI's Energy Access Explorer (EAE). <br/><br/><br/>"
            "To view more information about data quality standards, view the <a href='https://files.wri.org/d8/s3fs-public/energy-access-explorer-data-and-methods.pdf'><u>technical note</u>.</a>",
            style=style)
        p.wrap(2000, 2000)
        p.drawOn(page, 1030, 750)

        page.setFont(self.default_font_bold, 100)
        page.drawString(1030, 570, "Supported by")

        page.roundRect(
            1030, 60,
            920,
            460, 5, stroke=0, fill=1)

        cca_logo = absolute_path(
            'custom', 'static', 'img', 'cca.png')
        page.drawImage(cca_logo, 1040, 400,
                       height=100,
                       width=239,
                       preserveAspectRatio=True)

        aepc_logo = absolute_path(
            'custom', 'static', 'img', 'aepc.png')
        page.drawImage(aepc_logo, 1040, 255,
                       height=100,
                       width=605,
                       preserveAspectRatio=True)

        kartoza_logo = absolute_path(
            'custom', 'static', 'img', 'kartoza.png')
        page.drawImage(kartoza_logo, 1040, 105,
                       height=100,
                       width=322,
                       preserveAspectRatio=True)

        wri_logo = absolute_path(
            'custom', 'static', 'img', 'wri.png')
        page.drawImage(wri_logo, 1670, 400,
                       height=100,
                       width=240,
                       preserveAspectRatio=True)

        nou_logo = absolute_path(
            'custom', 'static', 'img', 'nou.png')
        page.drawImage(nou_logo, 1670, 255,
                       height=100,
                       width=100,
                       preserveAspectRatio=True)

        kth_logo = absolute_path(
            'custom', 'static', 'img', 'kth-240-white.png')
        page.drawImage(kth_logo, 1670, 105,
                       height=100,
                       width=100,
                       preserveAspectRatio=True)

        page.showPage()

    def draw_page_two(self, page):
        page.setFillColorRGB(0.349, 0.549, 0.286)
        page.rect(0,
                  0, self.page_width, self.page_height, stroke=0, fill=1)
        self._draw_title(page, '', self.use_case.name, False, (1, 1, 1))

        page.setFont(self.default_font_light, 25)
        y_pos = self._draw_wrapped_line(
            page,
            self.use_case.description,
            160,
            75,
            self.page_height - 175,
            35
        )
        page.setFont(self.default_font, 30)
        page.drawString(
            75, y_pos - 50,
            f'Scenario : {self.preset.name}')

        page.setFont(self.default_font_light, 25)
        y_pos = self._draw_wrapped_line(
            page,
            self.preset.description,
            90,
            75,
            y_pos - 100,
            35
        )

        urban_ratio = self.total_urban_population / self.total_population * 100 if self.total_urban_population > 0 else 0
        poverty_percentage = self.total_poverty / self.total_population * 100 if self.total_poverty > 0 else 0

        table_data = [
            ['', self.subregion],
            ['Population', '{:,}'.format(
                math.trunc(float(self.total_population)))],
            ['Households', '{:,}'.format(
                math.trunc(float(self.total_household)))],
            ['Urban ratio', '{:,.2f}%'.format(urban_ratio)],
            ['Population relying on\n\n\npolluting fuels and '
             'technologies',
             '{:,.2f}%'.format(self.total_cooking_percentage)],
            ['Portion under the poverty line',
             '{:,.2f}%'.format(poverty_percentage)]
        ]

        self._draw_supply_demand_table(page, y_pos)

        table_y = y_pos - 100
        for table_summary_data in self.table_summary_data:
            table_data.append(table_summary_data)
            table_y -= (50 * table_summary_data[0].count('\n\n\n')) + 50

        table_width = 1200
        table_x = 1100
        table_height = 1000

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (1, 0), self.default_font_bold),
            ('BACKGROUND', (0, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (1, -1), colors.Color(
                red=29 / 255, green=63 / 255, blue=116 / 255)),
            ('FONTSIZE', (0, 0), (1, -1), 23),
            ('RIGHTPADDING', (0, 0), (1, -1), 50),
            ('LEFTPADDING', (0, 0), (1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (1, -1), 30),
        ]

        table = Table(table_data, colWidths=[6.4 * inch, 4 * inch])
        table.setStyle(TableStyle(table_style))
        table.wrapOn(page, table_width, table_height)
        table.drawOn(page, table_x, self.table_supply_demand_y_pos)

        self._draw_footer(page, 2)
        page.showPage()

    def draw_map_page(
            self, page, map_image, title = '', legend_data = None,
            page_number=3):
        page.drawImage(
            map_image, 75, 30,
            width=1825,
            height=975,
            preserveAspectRatio=True,
            mask='auto')

        page.setFillColorRGB(1, 1, 1)
        page.rect(0, 0, self.page_width, self.navbar_height + 5,
                  stroke=0, fill=1)
        self._draw_footer(page, page_number)
        self._draw_title(page, '', title, False)

        if legend_data:
            legend_png_dir = os.path.join(settings.MEDIA_ROOT, 'legend_pngs')
            not os.path.exists(legend_png_dir) and os.mkdir(legend_png_dir)
            legend_png = os.path.join(
                legend_png_dir, f'{legend_data["name"]}.png')
            if not os.path.exists(legend_png):
                img_data = requests.get(legend_data['url']).content
                with open(legend_png, 'wb') as handler:
                    handler.write(img_data)
            legend_img = ImageReader(legend_png)
            page.drawImage(legend_img, 80, 60, mask='auto')

        page.showPage()

    def draw_page_three(self, page):
        self.draw_map_page(page, self.map_image, self.subregion)

    def draw_all_layers(self, page, page_number = 5):
        map_images = MapImage.objects.filter(
            preset=self.preset,
            boundary_uuid=self.boundary
        )
        for map_image in map_images:
            legend = (
                map_image.geonode_layer.link_set.filter(
                    name__icontains='legend').first()
            )
            legend_data = None
            if legend:
                legend_data = {
                    'name': map_image.geonode_layer.name,
                    'url': legend.url
                }
            title = 'Map Layer'
            try:
                title = (
                    self.categories.filter(
                        datasetfile__in=
                        map_image.geonode_layer.datasetfile_set.all()
                    ).first().name_long
                )
            except:  # noqa
                pass
            self.draw_map_page(page,
                               map_image.image.path,
                               title, legend_data, page_number)
            page_number += 1
            PageBreak()

    def draw_ccp_page(self, page, page_number = 3):
        if not self.demand_image:
            return

        self._draw_sidebar(page, (0.459, 0.714, 0.831))
        self._draw_footer(page, page_number)
        self._draw_title(page, 'Analysis', 'Clean Cooking Potential')
        self._draw_map(page, self.ccp_image, self.ccp_legend_path)
        self._draw_summary(page, self.demand_summary)

        page.setFillColorRGB(0, 0, 0)
        page.setFont(self.default_font_light, 25)
        self._draw_wrapped_line(
            page,
            'This index is an aggregated measure of all selected datasets '
            'under both the Demand and Supply categories. '
            'Identifies areas with higher energy demand and potential of '
            'supply which are characterized with higher index values.',
            100,
            100, 125, 40
        )

        page.showPage()

    def draw_supply_page(self, page, page_number):
        if not self.supply_image:
            return

        self._draw_sidebar(page)
        self._draw_footer(page, page_number)
        self._draw_title(page, 'Analysis', 'Supply index')
        self._draw_map(page, self.supply_image, self.supply_legend_path)
        self._draw_summary(page, self.supply_summary)

        page.setFillColorRGB(0, 0, 0)
        page.setFont(self.default_font_light, 25)
        self._draw_wrapped_line(
            page,
            'This index is an aggregated and weighted measure of all selected '
            'datasets under the Supply category. Identifies areas with '
            'potential for clean cooking energy supply.',
            100,
            75, 125, 40
        )

        page.showPage()


    def draw_ani_page(self, page, page_number = 3):
        if not self.ani_image:
            return

        self._draw_sidebar(page)
        self._draw_footer(page, page_number)
        self._draw_title(page, 'Analysis', 'Assistance Needed Index')
        self._draw_map(page, self.ani_image, self.ani_legend_path)
        self._draw_summary(page, self.ani_summary)

        page.setFillColorRGB(0, 0, 0)
        page.setFont(self.default_font_light, 25)
        self._draw_wrapped_line(
            page,
            'This index is an aggregated and weighted measure of '
            'selected datasets '
            'under both the Demand and Supply categories '
            'indicating existing or '
            'potential energy demand, low economic activity, '
            'and low access to '
            'infrastructure and resources.',
            100,
            75, 150, 40
        )

        page.showPage()

    def draw_supply_and_demand(self, page, page_number = 3):
        self._draw_footer(page, page_number)
        self._draw_title(
            page, 'Analysis', 'Demand Index and Supply Index', False)

        page.setFillColorRGB(87 / 255, 141 / 255, 68 / 255)
        page.setFont(self.default_font_bold, 30)
        page.drawString(
            75, self.page_height - 250,
            'Identifies areas with higher energy demand.')
        page.drawString(
            1100, self.page_height - 250,
            'Identifies areas with clean cooking supply potential.')

        self._draw_map(
            page, self.demand_image, self.demand_legend_path, 650, 80)
        self._draw_map(
            page, self.supply_image, self.supply_legend_path, 650, 1100)


        page.setFont(self.default_font, 25)
        page.setFillColorRGB(0, 0, 0)

        self._draw_wrapped_line(
            page,
            'This is an aggregated and weighted measure of all selected '
            'datasets under the Demand category. Identifies areas with '
            'higher energy demand.',
            70,
            75, self.page_height - 900, 40)

        self._draw_wrapped_line(
            page,
            'This index is an aggregated and weighted measure of all '
            'selected datasets under the Supply category. Identifies '
            'areas with potential for clean cooking energy supply.',
            70,
            1100, self.page_height - 900, 40)

        page.showPage()

    def post(self, request, *args, **kwargs):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        geo_id = request.POST.get('geoId', '')
        use_case_id = request.POST.get('useCaseId', None)
        preset_id = request.POST.get('scenarioId', None)
        boundary_id = request.POST.get('boundary', None)
        if boundary_id == 'null':
            boundary_id = None
        self.boundary = boundary_id

        self.map_image = request.POST.get('mapImage', '')
        self.demand_image = request.POST.get('demandImage', None)
        self.ccp_image = request.POST.get('ccpImage', None)
        self.ccp_tiff_file = request.POST.get('ccpTiff', None)
        self.demand_tiff_file = request.FILES.get('demandTiff', None)
        self.supply_tiff_file = request.FILES.get('supplyTiff', None)
        self.ani_tiff_file = request.FILES.get('aniTiff', None)
        self.supply_image = request.POST.get('supplyImage', None)
        self.ani_image = request.POST.get('aniImage', None)
        self.subregion = request.POST.get('subRegion', '')
        self.geography = Geography.objects.get(id=geo_id)
        self.table_summary_data = []

        self.demand_high_percentage = (
            request.POST.get('demandDataHighPercentage', '')
        )
        self.supply_high_percentage = (
            request.POST.get('supplyDataHighPercentage', '')
        )
        self.ani_med_high_total = (
            request.POST.get('aniDataMedToHigh', '')
        )
        if self.ani_med_high_total:
            self.ani_med_high_total = int(self.ani_med_high_total)
        else:
            self.ani_med_high_total = 0

        self.preset = Preset.objects.get(id=preset_id)

        self.summary_categories = SummaryReportCategory.objects.filter(
            preset=self.preset
        )

        if self.summary_categories.filter(analysis='ccp').exists():
            self.demand_summary = [
                {
                    'desc': self.preset.population_ccp_text,
                    'value': f'{self.demand_high_percentage}%'
                }
            ]
            if self.demand_tiff_file:
                demand_data = self._calculate_demand_supply(
                    self.demand_tiff_file,
                    'ccp'
                )
                for demand in demand_data:
                    self.demand_summary.append({
                        'desc': demand['label'],
                        'value': '{}'.format(demand['total_high'])
                    })

        if self.summary_categories.filter(analysis='supply').exists():
            self.supply_summary = [
                {
                    'desc': self.preset.population_supply_text,
                    'value': f'{self.supply_high_percentage}%'
                }
            ]

            if self.supply_tiff_file:
                supply_data = self._calculate_demand_supply(
                    self.supply_tiff_file,
                    'supply'
                )
                for supply in supply_data:
                    self.supply_summary.append({
                        'desc': supply['label'],
                        'value': '{}'.format(supply['total_high'])
                    })
                    self.table_summary_data.append([
                        f'Number of\n\n\n{supply["category"]}',
                        supply['total_in_raster']
                    ])

        if self.summary_categories.filter(analysis='ani').exists():
            self.ani_summary = [
                {
                    'desc': self.preset.population_ani_text,
                    'value':  '{:,.0f}'.format(self.ani_med_high_total)
                }
            ]
            ani_summary_data = self._calculate_ani_data(
                self.summary_categories.filter(analysis='ani')
            )
            for ani in ani_summary_data:
                self.ani_summary.append({
                    'desc': ani['label'],
                    'value': '{:,.0f}'.format(ani['total'])
                })

        self.total_population = int(
            request.POST.get('totalPopulation', '0')
        )

        if self.geography.household_layer:
            household_result = calculate_household(
                self.geography,
                boundary_id
            )
            if household_result:
                self.total_household = household_result['total_household']

        if self.geography.urban_layer:
            try:
                urban_result = calculate_urban(
                    self.geography,
                    boundary_id
                )
            except:  # noqa
                urban_result = None
            if urban_result:
                if urban_result['success']:
                    self.total_urban_population = (
                        urban_result['total_urban_population']
                    )
                    self.total_population = (
                        int(urban_result['total_population'])
                    )


        if self.geography.cooking_percentage_layer:
            try:
                cooking_percentage_result = calculate_cooking_with_traditional(
                    self.geography,
                    boundary_id
                )
            except:  # noqa
                cooking_percentage_result = None
            if cooking_percentage_result:
                if cooking_percentage_result['success']:
                    self.total_cooking_percentage = (
                        cooking_percentage_result['percentage']
                    )

        if self.geography.wealth_index_layer:
            try:
                poverty_result = calculate_poverty(
                    self.geography,
                    boundary_id
                )
            except:  # noqa
                poverty_result = None
            if poverty_result:
                if poverty_result['success']:
                    self.total_poverty = (
                        poverty_result['total_poverty_population']
                    )

        if use_case_id:
            try:
                self.use_case = UseCase.objects.get(id=use_case_id)
            except UseCase.DoesNotExist:
                pass

        parsed_url = urlparse(self.preset.permalink)
        captured_value = parse_qs(parsed_url.query)['inputs'][0]
        self.categories = category_from_url(captured_value.split(','))

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)
        p.setPageSize((self.page_width, self.page_height))

        self.draw_page_one(p)
        PageBreak()
        self.draw_page_two(p)
        PageBreak()

        current_page_number = 3

        if self.demand_summary:
            self.draw_ccp_page(p, current_page_number)
            current_page_number += 1
            PageBreak()

        if self.supply_summary:
            self.draw_supply_page(p, current_page_number)
            current_page_number += 1
            PageBreak()

        if self.ani_summary:
            self.draw_ani_page(p, current_page_number)
            current_page_number += 1
            PageBreak()

        # Check if the preset has supply and demand category
        if self.summary_categories.filter(analysis='supply_demand').exists():
            if self.demand_image and self.supply_image:
                self.draw_supply_and_demand(p, current_page_number)
                current_page_number += 1
                PageBreak()

        self.draw_all_layers(p, current_page_number)
        PageBreak()

        self.draw_page_end(p)
        PageBreak()

        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Report.pdf')
