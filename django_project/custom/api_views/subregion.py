import os.path

import requests
import xml.etree.ElementTree as ET

import zipfile
from django.http.response import Http404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from custom.models import Geography
from custom.tools.clip_layer import clip_vector_layer, clip_raster_layer
from geonode.layers.models import Layer


class SubregionListAPI(APIView):

    def get_property_list_from_geoserver(self, layer_name, property_name):
        url = f'{settings.GEOSERVER_PUBLIC_LOCATION}/wfs'
        params = {
            'service': 'wfs',
            'version': '2.0.0',
            'request': 'GetPropertyValue',
            'typeNames': layer_name,
            'valueReference': property_name
        }
        r = requests.get(url=url, params=params)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            subregion_list = []
            for child in root:
                value = child[0].text
                if value not in subregion_list:
                    subregion_list.append(value)
            subregion_list.sort()
            return subregion_list
        else:
            return None

    def get(self, request, geo_id, subregion_selector):
        try:
            geography = Geography.objects.get(
                id=geo_id
            )
        except Geography.DoesNotExist:
            raise Http404

        subregion_list = self.get_property_list_from_geoserver(
            layer_name=str(geography.vector_boundary_layer),
            property_name=subregion_selector
        )

        return Response({
            'geography': geography.name,
            'subregion_selector': subregion_selector,
            'subregion_list': subregion_list
        })


class ClipLayerByRegion(APIView):
    def post(self, request, *args):
        boundary_uuid = self.request.data.get('boundary', None)
        if '.tif' in boundary_uuid:
            boundary_uuid = boundary_uuid.replace('.tif', '')
        boundary_file = os.path.join(
            settings.MEDIA_ROOT,
            'rasterized',
            boundary_uuid + '.json'
        )
        if not os.path.exists(boundary_file):
            raise Http404

        layer_id = self.request.data.get('layer_id', None)
        try:
            layer = Layer.objects.get(id=layer_id)
        except Layer.DoesNotExist:
            raise Http404

        style_url = layer.default_style.sld_url
        output_folder = os.path.join(
            settings.MEDIA_ROOT,
            'clipped'
        )

        vector_layer = None
        raster_layer = None
        output = ''
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

        output = output.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)

        return Response({
            'success': (
                True if os.path.exists(output) and ( vector_layer or raster_layer ) else False
            ),
            'output': output,
            'style_url': style_url
        })
