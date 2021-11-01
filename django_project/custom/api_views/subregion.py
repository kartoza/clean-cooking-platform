import os.path
import json
import uuid

from celery.result import AsyncResult
import requests
import xml.etree.ElementTree as ET

import zipfile
from django.http.response import Http404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from custom.models import Geography, ClippedLayer
from geonode.layers.models import Layer


class SubregionListAPI(APIView):

    def get_property_list_from_geoserver(self, layer_name, property_name):
        cache_exist = False
        subregion_list = None

        url = f'{settings.GEOSERVER_PUBLIC_LOCATION}/wfs'
        params = {
            'service': 'wfs',
            'version': '2.0.0',
            'request': 'GetPropertyValue',
            'typeNames': layer_name,
            'valueReference': property_name
        }

        file_name = str(uuid.uuid3(
            uuid.NAMESPACE_DNS,
            f'{url}{json.dumps(params)}'))
        property_list_cached_dir = os.path.join(
            settings.MEDIA_ROOT,
            'property_list'
        )
        property_list_cached_file = os.path.join(
            property_list_cached_dir,
            file_name
        )
        if not os.path.exists(property_list_cached_dir):
            os.mkdir(property_list_cached_dir)

        if os.path.exists(property_list_cached_file):
            cache_exist = True
            subregion_list_file = open(property_list_cached_file)
            subregion_list = json.load(subregion_list_file)
            subregion_list_file.close()

        if not cache_exist:
            r = requests.get(url=url, params=params)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                subregion_list = []
                for child in root:
                    value = child[0].text
                    if value not in subregion_list:
                        subregion_list.append(value)
                subregion_list.sort()
            with open(property_list_cached_file, 'w+') as outfile:
                json.dump(subregion_list, outfile)

        return subregion_list

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
        from custom.tasks import clip_layer_by_region
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
        task_running = False

        try:
            layer = Layer.objects.get(id=layer_id)
        except Layer.DoesNotExist:
            raise Http404

        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=layer,
            boundary_uuid=boundary_uuid,
        )

        if not created:
            if clipped_layer.process_state and not clipped_layer.clipped_file:
                res = AsyncResult(clipped_layer.process_state)
                if res.ready():
                    return Response({
                        'status': 'Failed'
                    })
            if clipped_layer.clipped_file:
                style_url = layer.default_style.sld_url
                return Response({
                    'status': 'Success',
                    'output': f'{settings.MEDIA_URL}{clipped_layer.clipped_file.name}',
                    'style_url': style_url
                })

        if not task_running:
            clip_layer_by_region.delay(
                clipped_layer.id
            )

        return Response({
            'status': 'Pending'
        })
