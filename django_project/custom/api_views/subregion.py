import os.path

import requests
import xml.etree.ElementTree as ET
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

        output_folder = os.path.join(
            settings.MEDIA_ROOT,
            'clipped'
        )

        vector_layer = None
        raster_layer = None
        output = ''
        if 'Vector' in layer.display_type:
            vector_layer = layer.upload_session.layerfile_set.all().filter(
                name='shp'
            ).first()
        elif 'Raster' in layer.display_type:
            raster_layer = layer.upload_session.layerfile_set.all().filter(
                name='tif'
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
            )
            if not os.path.exists(output):
                layer_vector_file = os.path.join(
                    settings.MEDIA_ROOT,
                    vector_layer.file.name
                )
                clip_vector_layer(
                    layer_vector_file=layer_vector_file,
                    boundary_layer_file=boundary_file,
                    output_path=output)

        if raster_layer:
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
                    output_path=output)

        return Response({
            'success': (
                True if os.path.exists(output) and ( vector_layer or raster_layer ) else False
            ),
            'output': output
        })
