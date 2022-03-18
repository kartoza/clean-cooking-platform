import os.path
import time
import json

import requests
from pandas import json_normalize, DataFrame
from datetime import datetime

import numpy as np
from django.conf import settings

from custom.models import ClippedLayer, Category, DatasetFile
from custom.models.geography import Geography
from custom.tasks import clip_layer_by_region
from custom.tools.clip_layer import resize_raster_layer

from geonode.layers.models import Layer


def read_json(geojson_file):
    df = None
    if os.path.exists(geojson_file):
        with open(geojson_file) as f:
            try:
                data = json.load(f)
                df = json_normalize(data['features'])
            except UnicodeDecodeError:
                pass
    return df


def get_geojson_from_geoserver(layer: Layer):
    geojson_link = layer.link_set.filter(
        name__icontains='geojson').first()

    geojson_layer_dir = os.path.join(
        settings.MEDIA_ROOT,
        'geojson_layers'
    )
    if not os.path.exists(geojson_layer_dir):
        os.mkdir(geojson_layer_dir)

    geojson_file_path = os.path.join(
        geojson_layer_dir,
        f'{layer.name}.json'
    )

    if not os.path.exists(geojson_file_path):
        r = requests.get(url=geojson_link.url)
        with open(geojson_file_path, 'wb') as outfile:
            outfile.write(r.content)

    return geojson_file_path

def calculate_household(geography: Geography, boundary_id: str):

    if not geography:
        return None

    if not geography.household_layer:
        return None

    start_time = time.time()
    total_household = 0

    if boundary_id:
        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=geography.household_layer,
            boundary_uuid=boundary_id
        )
        if created or not clipped_layer.clipped_file:
            clipped_layer = clip_layer_by_region(
                clipped_layer.id
            )
        try:
            vector_file = clipped_layer.clipped_file.path
        except:  # noqa
            vector_file = settings.MEDIA_ROOT + str(clipped_layer.clipped_file)
    else:
        # find json file
        vector_file = get_geojson_from_geoserver(geography.household_layer)

    if 'json' in vector_file:
        features = read_json(vector_file)
        if isinstance(features, DataFrame) and not features.empty:
            total_household = features.sum()['properties.{}'.format(
                geography.household_layer_field)]

    return {
        'layer': vector_file,
        'execution_time': time.time() - start_time,
        'total_household': total_household
    }


def calculate_cooking_with_traditional(geography: Geography, boundary_id: str):

    start_time = time.time()
    percentage = 0

    if boundary_id:
        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=geography.cooking_percentage_layer,
            boundary_uuid=boundary_id
        )
        if created or not clipped_layer.clipped_file:
            clipped_layer = clip_layer_by_region(
                clipped_layer.id
            )
        vector_file = clipped_layer.clipped_file.path
    else:
        vector_file = get_geojson_from_geoserver(
            geography.cooking_percentage_layer)

    features = read_json(vector_file)
    if not features.empty:
        if boundary_id:
            # todo: get the largest area
            # features.sort_values(by='geometry', inplace=True,
            #                      key=lambda col: np.array(
            #                          [x.area for x in col]))
            percentage = features[
                'properties.{}'.format(
                    geography.cooking_percentage_layer_field
                )].iloc[-1]
        else:
            percentage =  features.mean()[
                'properties.{}'.format(
                    geography.cooking_percentage_layer_field
                )]

    return {
        'layer': vector_file,
        'success': True,
        'execution_time': time.time() - start_time,
        'percentage': percentage
    }


def _calculate_weight_average(
        boundary_id,
        input_layer,
        calculation='',
        calculate_population=False,
        alternate_population_layer=None):
    import rasterio
    import subprocess

    if not alternate_population_layer:
        # Get population-density layer
        category = Category.objects.filter(
            name_long__icontains='population'
        ).filter(
            name_long__icontains='density'
        ).first()

        dataset = DatasetFile.objects.filter(
            category=category,
            func='raster',
            geonode_layer__isnull=False
        ).first()
        population_layer = dataset.geonode_layer
    else:
        population_layer = alternate_population_layer

    if boundary_id:
        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=input_layer,
            boundary_uuid=boundary_id
        )
        if created or not clipped_layer.clipped_file:
            clipped_layer = clip_layer_by_region(
                clipped_layer.id
            )
        raster_file = clipped_layer.clipped_file.path

        population_clipped, _created = ClippedLayer.objects.get_or_create(
            layer=population_layer,
            boundary_uuid=boundary_id
        )

        if _created or not population_clipped.clipped_file.path:
            population_clipped = clip_layer_by_region(
                population_clipped.id
            )

        if not population_clipped or not raster_file:
            return {
                'success': False,
                'message': 'Missing population layer'
            }
        population_raster_file = population_clipped.clipped_file.path

    else:
        try:
            base_file = input_layer.get_base_file()[0].file
        except:  # noqa
            base_file = (
                input_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='tif'
                ).first().file
            )
        raster_file = base_file.path
        try:
            population_layer_file = population_layer.get_base_file()[0].file
        except:  # noqa
            population_layer_file = (
                population_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='tif'
                ).first().file
            )
        population_raster_file = population_layer_file.path

    if not boundary_id:
        resized_raster = raster_file.replace('.tif', '_resized.tif')
        if not os.path.exists(resized_raster):
            resize_raster_layer(
                raster_file, population_raster_file, resized_raster,
                srs=None)
        raster_file = resized_raster

    output = os.path.join(
        settings.MEDIA_ROOT,
        f'{boundary_id}_'
        f'{str(datetime.now().timestamp())}.tif'
    )

    command_output = subprocess.check_output([
        'gdal_calc.py',
        '-A',
        raster_file,
        '-B',
        population_raster_file,
        '--outfile',
        output,
        '--calc',
        calculation,
        '--NoDataValue',
        '0',
        '--overwrite',
    ], stderr=subprocess.STDOUT)

    total = 0
    total_population = 0
    if os.path.exists(output):
        src = rasterio.open(output)
        arr = src.read()
        arr[np.isinf(arr)] = 0
        total = np.nansum(arr)
        os.remove(output)

    if calculate_population:
        if os.path.exists(population_raster_file):
            src = rasterio.open(population_raster_file)
            arr = src.read()
            arr[np.isinf(arr)] = 0
            arr[np.isin(arr, [-99999])] = 0
            total_population = np.nansum(arr)

    return total, total_population, command_output


def calculate_urban(geography: Geography, boundary_id: str):
    start_time = time.time()
    total, total_population, command_output = _calculate_weight_average(
        boundary_id,
        geography.urban_layer,
        'B*logical_and(A>20,A<40)',
        True
    )
    return {
        'calculation': 'Total Population in Urban Area',
        'execution_time': time.time() - start_time,
        'total_population': total_population,
        'total_urban_population': total,
        'total_urban_percentage': total / total_population * 100,
        'output': command_output,
        'success': b'Error!' not in command_output
    }


def calculate_poverty(geography: Geography, boundary_id: str):
    start_time = time.time()
    total, total_population, command_output = _calculate_weight_average(
        boundary_id,
        geography.wealth_index_layer,
        'B*logical_and(A>0,A<50)',
        True
    )
    return {
        'calculation': 'Total Population in Poverty Area',
        'execution_time': time.time() - start_time,
        'total_poverty_population': total,
        'total_poverty_percentage': total / total_population * 100,
        'output': command_output,
        'success': b'Error!' not in command_output
    }


def calculate_poverty_supply_layer_distance(
        geography: Geography,
        boundary_id: str,
        supply_layer: Layer,
        percentage: bool = False):
    """Calculate total population under poverty line close to supply layer"""

    start_time = time.time()
    from osgeo import gdal

    if boundary_id:
        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=supply_layer,
            boundary_uuid=boundary_id
        )
        if (
            created or
            not clipped_layer.clipped_file or
            not os.path.exists(clipped_layer.clipped_file.path)):
            clipped_layer = clip_layer_by_region(
                clipped_layer.id
            )
        raster_file = clipped_layer.clipped_file
    else:
        try:
            raster_file = supply_layer.get_base_file()[0].file
        except:  # noqa
            raster_file = (
                supply_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='tif'
                ).first().file
            )

    gtif = gdal.Open(raster_file.path)
    srcband = gtif.GetRasterBand(1)

    # Get raster statistics
    stats = srcband.GetStatistics(True, True)

    highest = stats[1]
    min_range = ( highest / 5 ) * 4

    total, _, command_output = _calculate_weight_average(
        boundary_id,
        supply_layer,
        f'B*logical_and(A>{min_range},A<={highest})',
        False,
        geography.wealth_index_layer
    )

    value = '{:,.0f}'.format(total)

    if percentage:
        total_all, _, _ = _calculate_weight_average(
            boundary_id,
            supply_layer,
            f'B*logical_and(A>{stats[0]},A<={highest})',
            False,
            geography.wealth_index_layer
        )
        percentage_value = total / total_all * 100
        value =  '{:,.2f}%'.format(percentage_value)

    return {
        'result': "[ STATS ] =  Minimum=%.3f, "
                   "Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (
    stats[0], stats[1], stats[2], stats[3]),
        'execution_time': time.time() - start_time,
        'highest_min_range': min_range,
        'total': total,
        'value': value,
        'output': command_output,
        'success': b'Error!' not in command_output
    }
