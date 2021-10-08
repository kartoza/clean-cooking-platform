import os.path
import random
from osgeo import gdal
from osgeo import ogr

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
        feature.SetField(field_index, random.randint(0, 255))
        source_layer.SetFeature(feature)
        if feature.geometry():
            feature.geometry().CloseRings()
            feat = feature.geometry()
            feat.CloseRings()
            wkt = feat.ExportToWkt()
            multi.AddGeometryDirectly(ogr.CreateGeometryFromWkt(wkt))
    union = multi.UnionCascaded()
    geojson = union.Simplify(0.001).ExportToJson()
    geojson_destination = destination_path.replace('.tif', '.json')
    if os.path.exists(geojson_destination):
        os.remove(geojson_destination)
    with open(geojson_destination, 'w') as json_file:
        json_file.write(geojson)

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('GTiff').Create(
        destination_path, x_res,
        y_res, 3, gdal.GDT_Float32)
    target_ds.SetGeoTransform((
        x_min, pixel_size, 0,
        y_max, 0, -pixel_size,
    ))
    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    nodata_value = -999999
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(nodata_value)
    band.FlushCache()

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, (3, 2, 1), source_layer,
                              burn_values=(0, 0, 0),
                              options=["ATTRIBUTE=%s" % RASTERIZE_COLOR_FIELD])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
