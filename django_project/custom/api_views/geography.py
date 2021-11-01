# coding=utf-8
import os.path
import uuid
import zipfile

import requests
from django.conf import settings
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from custom.models import Category
from custom.models.geography import Geography
from custom.serializers.geography_serializer import GeographySerializer
from custom.tools.rasterize_layer import rasterize_layer


class GeographyDetail(APIView):

    def get(self, request, *args):
        name = self.request.GET.get('name', None)
        geo = self.request.GET.get('geo', None)
        filters = {}
        if name:
            filters = {
                'name__iexact': name
            }
        if geo:
            filters = {
                'id': geo
            }
        if filters:
            geography = Geography.objects.get(
                **filters
            )
            return Response(
                GeographySerializer(geography, many=False).data
            )
        raise Http404


class GeographyList(APIView):

    def get(self, request, *args):
        geo = self.request.GET.get('geo', None)
        additional_filters = {}
        if geo:
            additional_filters = {
                'id': geo,
                'parent__id': geo
            }
        return Response(
            GeographySerializer(Geography.objects.filter(
                online=True,
                **additional_filters
            ), many=True).data
        )


class GeographyRasterMask(APIView):

    def post(self, request, *args):
        geo_id = self.request.data.get('geo_id', None)
        subregion_selector = self.request.data.get('subregion_selector', None)
        subregion_value = self.request.data.get('subregion_value', None)
        try:
            geo = Geography.objects.get(id=geo_id)
        except Geography.DoesNotExist:
            raise Http404

        raster_dir = os.path.join(settings.MEDIA_ROOT, 'rasterized')
        if not os.path.exists(raster_dir):
            os.mkdir(raster_dir)

        raster_shp_dir = os.path.join(raster_dir, 'shp')
        if not os.path.exists(raster_shp_dir):
            os.mkdir(raster_shp_dir)

        raster_tif_dir = os.path.join(raster_dir, 'tif')
        if not os.path.exists(raster_tif_dir):
            os.mkdir(raster_tif_dir)

        boundary_layer_name = str(geo.vector_boundary_layer)
        shp_file = None
        raster_shp_zip_dir = os.path.join(
            raster_shp_dir, boundary_layer_name)
        if not os.path.exists(raster_shp_zip_dir):
            os.mkdir(raster_shp_zip_dir)
        else:
            for unzipped_file in os.listdir(raster_shp_zip_dir):
                if unzipped_file.endswith('.shp'):
                    shp_file = os.path.join(
                        raster_shp_zip_dir,
                        unzipped_file
                    )
        shp_zip_file = os.path.join(
            raster_shp_zip_dir,
            boundary_layer_name + '.zip')

        if not shp_file:
            # Download zipped shp file from geoserver
            url = f'{settings.GEOSERVER_PUBLIC_LOCATION}/ows'
            params = {
                'service': 'WFS',
                'version': '1.0.0',
                'request': 'GetFeature',
                'typeNames': str(geo.vector_boundary_layer),
                'outputFormat': 'SHAPE-ZIP',
                'srs': 'EPSG:4326'
            }
            r = requests.get(url=url, params=params, stream=True)
            chunk_size = 2000
            with open(shp_zip_file, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            with zipfile.ZipFile(shp_zip_file, 'r') as zip_ref:
                zip_ref.extractall(raster_shp_zip_dir)
            for unzipped_file in os.listdir(raster_shp_zip_dir):
                if unzipped_file.endswith('.shp'):
                    shp_file = os.path.join(raster_shp_zip_dir, unzipped_file)
            os.remove(shp_zip_file)

        raster_source_dir = raster_shp_zip_dir.replace('shp', 'tif')

        if not os.path.exists(raster_source_dir):
            os.mkdir(raster_source_dir)

        raster_source_file = os.path.join(
            raster_source_dir,
            boundary_layer_name + '.tif'
        )

        if not os.path.exists(raster_source_file):
            url = f'{settings.GEOSERVER_PUBLIC_LOCATION}/wcs'
            params = {
                'service': 'WCS',
                'version': '2.0.1',
                'request': 'GetCoverage',
                'coverageid': geo.raster_mask_layer.typename.replace(':', '__'),
                'format': 'image/tiff',
                'srs': 'EPSG:4326',
                'bbox': geo.raster_mask_layer.bbox_string
            }
            r = requests.get(url=url, params=params, stream=True)
            chunk_size = 2000
            with open(raster_source_file, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)

        uuid_string = str(uuid.uuid3(
            uuid.NAMESPACE_OID,
            f'{shp_file}{subregion_selector}{subregion_value}'
        )) + '.tif'

        destination_path = os.path.join(
            raster_dir,
            uuid_string,
        )
        where_condition = f"{subregion_selector}='{subregion_value}'"

        if (
            os.path.exists(shp_file)
        ):
            try:
                rasterize_layer(
                    shp_file,
                    raster_source_file,
                    1000,
                    destination_path,
                    where_condition
                )
            except Exception as e: # noqa
                raise Http404

        all_layer_ids = []
        all_category = Category.objects.filter(
            geography__id=geo_id,
            boundary_layer=False,
            online=True
        )
        for category in all_category:
            for dataset in category.datasetfile_set.all():
                if dataset.geonode_layer:
                    all_layer_ids.append(dataset.geonode_layer.id)

        return Response({
            'Success': True,
            'Geo': geo.name,
            'RasterPath': f'{settings.MEDIA_URL}rasterized/{uuid_string}',
            'File': uuid_string,
            'AllLayerIds': all_layer_ids
        })
