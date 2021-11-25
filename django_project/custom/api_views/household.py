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
from custom.tools.calculate_household import calculate_household
from custom.tools.rasterize_layer import rasterize_layer


class CalculateHousehold(APIView):

    def get(self, request, *args):
        geo_id = request.GET.get('geoId', None)
        boundary = request.GET.get('boundary', '')
        geography = Geography.objects.get(id=geo_id)

        result = calculate_household(geography, boundary)

        return Response(result)
