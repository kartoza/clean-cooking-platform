# coding=utf-8
import os
import logging

import requests
import zipfile

from django.conf import settings
from custom.celery import app

from custom.tools.clip_layer import clip_vector_layer, clip_raster_layer

logger = logging.getLogger(__name__)


@app.task(bind=True, name='custom.tasks.clip_layer_by_region', queue='update')
def clip_layer_by_region(self, clipped_layer_id):
    from custom.models.clipped_layer import ClippedLayer

    clipped_layer = ClippedLayer.objects.get(
        id=clipped_layer_id
    )
    layer = clipped_layer.layer
    boundary_uuid = clipped_layer.boundary_uuid
    clipped_layer.process_state = self.request.id
    clipped_layer.save()

    logger.info('Clipping layer {}'.format(clipped_layer.id))
    logger.info('Geonode layer {}'.format(layer.id))

    boundary_file = os.path.join(
        settings.MEDIA_ROOT,
        'rasterized',
        boundary_uuid + '.json'
    )

    output_folder = os.path.join(
        settings.MEDIA_ROOT,
        'clipped'
    )

    output = None
    vector_layer = None
    raster_layer = None
    if 'Vector' in layer.display_type:
        vector_layer = layer.upload_session.layerfile_set.all().filter(
            file__icontains='shp'
        ).first()
    elif 'Raster' in layer.display_type:
        raster_layer = layer.upload_session.layerfile_set.all().filter(
            file__icontains='tif'
        ).first()

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    output_path_folder = os.path.join(
        output_folder,
        f'{str(layer)}:{boundary_uuid}'
    )

    if not os.path.exists(output_path_folder):
        os.mkdir(output_path_folder)

    if vector_layer:
        clipped_layer.layer_type = 'vector'
        output = (
            os.path.join(
                output_path_folder,
                os.path.basename(vector_layer.file.name))
        ).replace('shp', 'json')
        if not os.path.exists(output):
            layer_vector_file = os.path.join(
                settings.MEDIA_ROOT,
                vector_layer.file.name
            )
            if not os.path.exists(layer_vector_file):
                # Download file
                layer_temp_folder = os.path.join(
                    settings.MEDIA_ROOT,
                    'layers',
                    'temp'
                )
                if not os.path.exists(layer_temp_folder):
                    os.mkdir(layer_temp_folder)
                layer_name = os.path.basename(vector_layer.file.name)
                layer_vector_dir = os.path.join(
                    layer_temp_folder,
                    layer.name
                )
                if not os.path.exists(layer_vector_dir):
                    os.mkdir(layer_vector_dir)
                    layer_vector_file = None
                else:
                    for unzipped_file in os.listdir(layer_vector_dir):
                        if unzipped_file.endswith('.shp'):
                            layer_vector_file = os.path.join(
                                layer_vector_dir,
                                unzipped_file)
                            break

                if not layer_vector_file:
                    shp_zip_file = os.path.join(
                        layer_vector_dir,
                        layer_name.replace('.shp', '.zip')
                    )
                    url = f'{settings.GEOSERVER_PUBLIC_LOCATION}/ows'
                    params = {
                        'service': 'WFS',
                        'version': '1.0.0',
                        'request': 'GetFeature',
                        'typeNames': str(layer),
                        'outputFormat': 'SHAPE-ZIP',
                        'srs': 'EPSG:4326'
                    }
                    r = requests.get(url=url, params=params, stream=True)
                    chunk_size = 2000
                    with open(shp_zip_file, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size):
                            fd.write(chunk)
                    with zipfile.ZipFile(shp_zip_file, 'r') as zip_ref:
                        zip_ref.extractall(layer_vector_dir)
                    for unzipped_file in os.listdir(layer_vector_dir):
                        if unzipped_file.endswith('.shp'):
                            layer_vector_file = os.path.join(layer_vector_dir,
                                                             unzipped_file)
                    os.remove(shp_zip_file)

            clip_vector_layer(
                layer_vector_file=layer_vector_file,
                boundary_layer_file=boundary_file,
                output_path=output)

    if raster_layer:
        clipped_layer.layer_type = 'raster'
        raster_boundary_file = boundary_file.replace('.json', '.tif')
        if not os.path.exists(raster_boundary_file):
            raster_boundary_file = None
        output = (
            os.path.join(
                output_path_folder,
                os.path.basename(raster_layer.file.name))
        )
        if not os.path.exists(output):
            layer_raster_file = os.path.join(
                settings.MEDIA_ROOT,
                raster_layer.file.name
            )
            clip_raster_layer(
                layer_raster_file=layer_raster_file,
                boundary_layer_file=boundary_file,
                output_path=output,
                raster_boundary_file=raster_boundary_file)

    if output:
        clipped_layer.clipped_file.name = output.replace(
            settings.MEDIA_ROOT,
            ''
        )
    logger.info('Finish clipping layer')
    logger.info('Output {}'.format(output))
    clipped_layer.save()
