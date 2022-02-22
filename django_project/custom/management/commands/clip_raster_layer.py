# coding=utf-8
import os
from django.core.management.base import BaseCommand
from custom.tools.clip_layer import clip_raster_layer


class Command(BaseCommand):
    """Update all map to have map slugs.
    """
    args = ''
    help = 'Clip raster layer'

    def handle(self, *args, **options):
        boundary_uuid = '44a3c25c-c6f2-329e-9199-2280aeededac'
        output_path = f'/home/web/media/clipped.tif'
        boundary_layer_file = f'/home/web/media/rasterized/{boundary_uuid}.json'
        # boundary_layer_file = f'/home/web/media/boundary_json.geojson'
        if os.path.exists(output_path):
            os.remove(output_path)

        clip_raster_layer(
            layer_raster_file='/home/web/media/layers/2022/02/01/population_npl_2018_10_01.tif',
            boundary_layer_file=boundary_layer_file,
            output_path=output_path,
            raster_boundary_file='/home/web/media/rasterized/44a3c25c-c6f2-329e-9199-2280aeededac.tif'
        )
