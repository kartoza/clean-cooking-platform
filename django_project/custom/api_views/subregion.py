import requests
import xml.etree.ElementTree as ET
from django.http.response import Http404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from custom.models import Geography


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
