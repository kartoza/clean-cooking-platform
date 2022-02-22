import os.path
import json
import random
from osgeo import gdal
from osgeo import ogr
from shapely.geometry import shape, JOIN_STYLE, mapping

from custom.tools.clip_layer import clip_vector_layer, clip_raster_layer

RASTERIZE_COLOR_FIELD = "__color__"


# example GDAL error handler function
def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.CE_None:'None',
            gdal.CE_Debug:'Debug',
            gdal.CE_Warning:'Warning',
            gdal.CE_Failure:'Failure',
            gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print('Error Number: %s' % (err_num))
    print('Error Type: %s' % (err_class))
    print('Error Message: %s' % (err_msg))


def rasterize_layer(
        source_shp,
        raster_source_file,
        pixel_size = 100,
        destination_path = '',
        where = ''):
    # Open the data source
    gdal.PushErrorHandler(gdal_error_handler)
    orig_data_source = ogr.Open(source_shp)
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(
        orig_data_source, "")

    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(RASTERIZE_COLOR_FIELD, ogr.OFTReal)
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(RASTERIZE_COLOR_FIELD)
    source_layer.SetAttributeFilter(where)
    x_min, x_max, y_min, y_max = source_layer.GetExtent()

    multi = ogr.Geometry(ogr.wkbMultiPolygon)

    for feature in source_layer:
        try:
            feature.SetField(field_index, random.randint(0, 255))
            source_layer.SetFeature(feature)
            if feature.geometry():
                feature.geometry().CloseRings()
                feat = feature.geometry()
                if feat.GetGeometryType() == ogr.wkbMultiPolygon:
                    for polygon in feat:
                        polygon.CloseRings()
                        wkt = polygon.ExportToWkt()
                        multi.AddGeometryDirectly(
                            ogr.CreateGeometryFromWkt(wkt))
                else:
                    feat.CloseRings()
                    wkt = feat.ExportToWkt()
                    multi.AddGeometryDirectly(ogr.CreateGeometryFromWkt(wkt))
        except Exception as e:
            continue
    union = multi.UnionCascaded()
    geojson = union.ExportToJson()
    geojson_destination = destination_path.replace('.tif', '.json')
    if os.path.exists(geojson_destination):
        os.remove(geojson_destination)

    poly = shape(json.loads(geojson))
    fx = poly.buffer(
        0.001, 1, join_style=JOIN_STYLE.mitre).buffer(
        -0.001, 1, join_style=JOIN_STYLE.mitre)
    geojson = json.dumps(mapping(fx))

    with open(geojson_destination, 'w') as json_file:
        json_file.write(geojson)

    err = 0
    clip_raster_layer(
        layer_raster_file=raster_source_file,
        boundary_layer_file=json_file.name,
        output_path=destination_path)

    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
