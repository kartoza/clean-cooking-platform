import json
import time
import os
import logging
import shutil

from osgeo import gdal, ogr, osr
import subprocess
import numpy as np

logger = logging.getLogger(__name__)

# Enable GDAL/OGR exceptions
gdal.UseExceptions()

# GDAL & OGR memory drivers
GDAL_MEMORY_DRIVER = gdal.GetDriverByName('MEM')
OGR_MEMORY_DRIVER = ogr.GetDriverByName('Memory')
MAX_VALIDATE_TRY = 100


def clip_vector_layer(
        layer_vector_file = '',
        boundary_layer_file = '',
        output_path = ''):

    validated = True
    output_path = output_path.replace('shp', 'json')

    if os.path.exists(output_path):
        basename = os.path.basename(output_path)
        basename = basename.replace('.shp', '')
        basename = basename.replace('.json', '')
        for file_name in os.listdir(os.path.dirname(output_path)):
            if basename in file_name:
                os.remove(os.path.join(os.path.dirname(output_path), file_name))

    subprocess.run([
        'ogr2ogr',
        '-f',
        'GeoJSON',
        '-clipsrc',
        boundary_layer_file,
        output_path,
        layer_vector_file])

    return validated


def resize_raster_layer(
        input_layer, boundary_layer, output, srs=None, keep_resized_name=False):
    raster_boundary = gdal.Open(boundary_layer, gdal.GA_ReadOnly)

    if not srs:
        dataset = gdal.Open(input_layer, gdal.GA_ReadOnly)
        projection = dataset.GetProjection()

        srs = osr.SpatialReference()
        srs.ImportFromWkt(projection)

    if os.path.exists(output):
        os.remove(output)
    subprocess.run([
        'gdalwarp',
        '-of',
        'GTiff',
        '-s_srs',
        f'{srs.GetAuthorityName(None)}:{srs.GetAuthorityCode(None)}',
        '-t_srs',
        'epsg:4326',
        '-ts',
        f'{raster_boundary.RasterXSize}',
        f'{raster_boundary.RasterYSize}',
        input_layer,
        output])


def clip_raster_layer(layer_raster_file, boundary_layer_file, output_path, raster_boundary_file = None):
    # Taken and slightly modified from https://gis.stackexchange.com/a/200753
    # Get coords for bounding box
    boundary_source = ogr.Open(boundary_layer_file)
    boundary_layer = boundary_source.GetLayer(0)
    extent = boundary_layer.GetExtent()
    min_x, max_x, min_y, max_y = extent[0], extent[1], extent[2], extent[3]

    # Open original data as read only
    dataset = gdal.Open(layer_raster_file, gdal.GA_ReadOnly)

    bands = dataset.RasterCount

    # Getting georeference info
    transform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    x_origin = transform[0]
    y_origin = transform[3]
    pixel_width = transform[1]
    pixel_height = -transform[5]

    # Getting spatial reference of input raster
    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)

    # WGS84 projection reference
    OSR_WGS84_REF = osr.SpatialReference()
    OSR_WGS84_REF.ImportFromEPSG(4326)

    # OSR transformation
    wgs84_to_image_transformation = osr.CoordinateTransformation(OSR_WGS84_REF,
                                                                srs)
    xy_min = wgs84_to_image_transformation.TransformPoint(min_x, max_y)
    xy_max = wgs84_to_image_transformation.TransformPoint(max_x, min_y)

    # Computing Point1(i1,j1), Point2(i2,j2)
    i1 = int((xy_min[0] - x_origin) / pixel_width)
    j1 = int((y_origin - xy_min[1]) / pixel_height)
    i2 = int((xy_max[0] - x_origin) / pixel_width)
    j2 = int((y_origin - xy_max[1]) / pixel_height)
    new_cols = i2 - i1 + 1
    new_rows = j2 - j1 + 1

    # New upper-left X,Y values
    new_x = x_origin + i1 * pixel_width
    new_y = y_origin - j1 * pixel_height
    new_transform = (new_x, transform[1], transform[2], new_y, transform[4],
                     transform[5])

    for feature in boundary_layer:
        wkt_geom = ogr.CreateGeometryFromWkt(str(feature.geometry()))
        wkt_geom.Transform(wgs84_to_image_transformation)
        break

    target_ds = GDAL_MEMORY_DRIVER.Create('', new_cols, new_rows, 1,
                                          gdal.GDT_Byte)
    target_ds.SetGeoTransform(new_transform)
    target_ds.SetProjection(projection)

    # Create a memory layer to rasterize from.
    ogr_dataset = OGR_MEMORY_DRIVER.CreateDataSource('shapemask')
    ogr_layer = ogr_dataset.CreateLayer('shapemask', srs=srs)
    ogr_feature = ogr.Feature(ogr_layer.GetLayerDefn())
    ogr_feature.SetGeometryDirectly(ogr.Geometry(wkt=wkt_geom.ExportToWkt()))
    ogr_layer.CreateFeature(ogr_feature)

    gdal.RasterizeLayer(target_ds, [1], ogr_layer, burn_values=[1],
                        options=["ALL_TOUCHED=TRUE"])

    # Create output file
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_path, new_cols, new_rows, bands,
                          gdal.GDT_Float32)

    # Read in bands and store all the data in bandList
    mask_array = target_ds.GetRasterBand(1).ReadAsArray()
    band_list = []

    for i in range(bands):
        band_list.append(
            dataset.GetRasterBand(i + 1).ReadAsArray(
                i1, j1, new_cols, new_rows))

    for j in range(bands):
        data = np.where(mask_array == 1, band_list[j], mask_array)
        out_ds.GetRasterBand(j + 1).SetNoDataValue(0)
        out_ds.GetRasterBand(j + 1).WriteArray(data)

    out_ds.SetProjection(projection)
    out_ds.SetGeoTransform(new_transform)

    target_ds = None
    dataset = None
    out_ds = None
    ogr_dataset = None

    # Resize the layer if it has different width and height with boundary
    if raster_boundary_file:
        raster_boundary = gdal.Open(raster_boundary_file, gdal.GA_ReadOnly)
        output_path_resized = output_path.replace('.tif', '_resized.tif')
        if os.path.exists(output_path_resized):
            os.remove(output_path_resized)
        subprocess.run([
            'gdalwarp',
            '-of',
            'GTiff',
            '-s_srs',
            f'{srs.GetAuthorityName(None)}:{srs.GetAuthorityCode(None)}',
            '-t_srs',
            'epsg:4326',
            '-ts',
            f'{raster_boundary.RasterXSize}',
            f'{raster_boundary.RasterYSize}',
            output_path,
            output_path_resized])
        if os.path.exists(output_path_resized):
            shutil.move(output_path_resized, output_path)

