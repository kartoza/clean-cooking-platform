import os.path
import json
import uuid

from celery.result import AsyncResult
import requests
import xml.etree.ElementTree as ET

from django.http.response import Http404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from custom.models import Geography, ClippedLayer, SUCCESS, PENDING, FAILED
from geonode.layers.models import Layer


class SubregionListAPI(APIView):

    def get_property_list_from_geoserver(self,
                                         geography,
                                         property_name,
                                         property_value = None):
        cache_exist = False
        subregion_list = None
        layer_name = str(geography.vector_boundary_layer)

        url = f'{settings.GEOSERVER_PUBLIC_LOCATION}/wfs'
        params = {
            'service': 'wfs',
            'version': '2.0.0',
            'request': 'GetPropertyValue',
            'typeNames': layer_name,
            'valueReference': property_name
        }

        if property_value:
            params['cql_filter'] = f"{property_name}='{property_value}'"

            # Change the valueReference to the child of the selector, to get
            # all descendant values
            if property_name == geography.province_selector:
                params['valueReference'] = geography.district_selector
            elif property_name == geography.district_selector:
                params['valueReference'] = geography.municipal_selector

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

        if not cache_exist or not subregion_list:
            r = requests.get(url=url, params=params)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                subregion_list = []
                for child in root:
                    value = child[0].text
                    if value not in subregion_list:
                        if isinstance(value, str):
                            subregion_list.append(value)
                subregion_list.sort()
            with open(property_list_cached_file, 'w+') as outfile:
                json.dump(subregion_list, outfile)

        return subregion_list

    def get(self, request, geo_id, subregion_selector, subregion_value = None):
        try:
            geography = Geography.objects.get(
                id=geo_id
            )
        except Geography.DoesNotExist:
            raise Http404

        subregion_list = self.get_property_list_from_geoserver(
            geography=geography,
            property_name=subregion_selector,
            property_value=subregion_value
        )

        return Response({
            'geography': geography.name,
            'subregion_selector': subregion_selector,
            'subregion_value': subregion_value,
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
        response_status = ''

        try:
            layer = Layer.objects.get(id=layer_id)
        except Layer.DoesNotExist:
            raise Http404

        try:
            clipped_layer, created = ClippedLayer.objects.get_or_create(
                layer=layer,
                boundary_uuid=boundary_uuid,
            )
        except ClippedLayer.MultipleObjectsReturned:
            clipped_layers = ClippedLayer.objects.filter(
                layer=layer, boundary_uuid=boundary_uuid)
            created = False
            clipped_layer = clipped_layers.last()
            clipped_layers.exclude(id=clipped_layer.id).delete()

        try:
            style_url = layer.default_style.sld_url
        except AttributeError:
            style_url = ''

        if not created:
            if clipped_layer.failed:
                response_status = FAILED
            elif clipped_layer.successful:
                response_status = SUCCESS
            elif clipped_layer.pending:
                res = AsyncResult(clipped_layer.process_state)
                if res.ready(): # Task already finished
                    if clipped_layer.clipped_file:
                        clipped_layer.state = SUCCESS
                        clipped_layer.save()
                        response_status = SUCCESS
                else:
                    response_status = PENDING

        if not response_status:
            clipped_layer.state = PENDING
            clipped_layer.save()
            response_status = PENDING
            clip_layer_by_region.delay(
                clipped_layer.id
            )

        response_data = {}
        if response_status == SUCCESS:
            response_data = {
                'output': f'{settings.MEDIA_URL}'
                          f'{clipped_layer.clipped_file.name}',
                'style_url': style_url
            }

        return Response({
            'status': response_status,
            **response_data
        })
