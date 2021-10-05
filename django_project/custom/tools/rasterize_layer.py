import random
from osgeo import gdal
from osgeo import ogr

RASTERIZE_COLOR_FIELD = "__color__"


def rasterize_layer(
        source_shp,
        pixel_size = 0.01,
        destination_path = '',
        where = ''):
    # Open the data source
    orig_data_source = ogr.Open(source_shp)
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(
        orig_data_source, "")
    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(RASTERIZE_COLOR_FIELD, ogr.OFTReal)
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(RASTERIZE_COLOR_FIELD)
    source_layer.SetAttributeFilter(where)

    for feature in source_layer:
        feature.SetField(field_index, random.randint(0, 255))
        source_layer.SetFeature(feature)
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
