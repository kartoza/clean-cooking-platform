import os.path
import time
from datetime import datetime

import numpy as np
from django.conf import settings

from custom.models import ClippedLayer, Category, DatasetFile
from custom.models.geography import Geography
from custom.tasks import clip_layer_by_region
from custom.tools.clip_layer import resize_raster_layer


def calculate_household(geography: Geography, boundary_id: str):
    import geopandas as gpd

    if not geography:
        return None

    if not geography.household_layer:
        return None

    start_time = time.time()

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
        try:
            base_file = geography.household_layer.get_base_file()[0].file
        except:  # noqa
            base_file = (
                geography.household_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='shp'
                ).first().file
            )
        vector_file = base_file.path
    features = gpd.read_file(vector_file)
    total_household = features.sum()[geography.household_layer_field]

    return {
        'layer': vector_file,
        'execution_time': time.time() - start_time,
        'total_household': total_household
    }


def calculate_cooking_with_traditional(geography: Geography, boundary_id: str):
    import geopandas as gpd

    start_time = time.time()

    if boundary_id:
        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=geography.cooking_percentage_layer,
            boundary_uuid=boundary_id
        )
        if created or not clipped_layer.clipped_file:
            clipped_layer = clip_layer_by_region(
                clipped_layer.id
            )
        vector_file = clipped_layer.clipped_file
    else:
        try:
            base_file = geography.cooking_percentage_layer.get_base_file()[0].file
        except:  # noqa
            base_file = (
                geography.cooking_percentage_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='shp'
                ).first().file
            )
        vector_file = base_file

    features = gpd.read_file(vector_file.path)
    if boundary_id:
        features.sort_values(by='geometry', inplace=True,
                             key=lambda col: np.array([x.area for x in col]))
        percentage = features[geography.cooking_percentage_layer_field].iloc[-1]
    else:
        percentage =  features.mean()[geography.cooking_percentage_layer_field]

    return {
        'layer': vector_file.url,
        'success': True,
        'execution_time': time.time() - start_time,
        'percentage': percentage
    }


def _calculate_weight_average(boundary_id, input_layer, calculation='',
                              calculate_population=False):
    import rasterio
    import subprocess
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

        population_clipped = ClippedLayer.objects.filter(
            layer=dataset.geonode_layer,
            boundary_uuid=boundary_id
        ).first()

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
            population_layer = dataset.geonode_layer.get_base_file()[0].file
        except:  # noqa
            population_layer = (
                dataset.geonode_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='tif'
                ).first().file
            )
        population_raster_file = population_layer.path

    if not boundary_id:
        resized_raster = raster_file.replace('.tif', '_resized.tif')
        if not os.path.exists(resized_raster):
            resize_raster_layer(
                raster_file, population_raster_file, resized_raster,
                srs=None)
        raster_file = resized_raster

    output = os.path.join(
        settings.MEDIA_ROOT,
        f'{boundary_id}_{category.geography.id}_'
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
        arr[np.isnan(arr)] = 0
        total = arr.sum()

    if calculate_population:
        if os.path.exists(population_raster_file):
            src = rasterio.open(population_raster_file)
            arr = src.read()
            arr[np.isnan(arr)] = 0
            total_population = arr.sum()

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
        'output': command_output,
        'success': b'Error!' not in command_output
    }


def calculate_poverty(geography: Geography, boundary_id: str):
    start_time = time.time()
    total, total_population, command_output = _calculate_weight_average(
        boundary_id,
        geography.wealth_index_layer,
        'B*logical_and(A>0,A<50)',
    )
    return {
        'calculation': 'Total Population in Poverty Area',
        'execution_time': time.time() - start_time,
        'total_poverty_population': total,
        'output': command_output,
        'success': b'Error!' not in command_output
    }
