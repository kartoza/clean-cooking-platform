from geonode.layers.models import Layer
from rest_framework.response import Response
from rest_framework.views import APIView

from custom.models.geography import Geography
from custom.tools.report_calculation import (
    calculate_household,
    calculate_urban, calculate_cooking_with_traditional,
    calculate_poverty,
    calculate_poverty_supply_layer_distance
)


class CalculateReport(APIView):

    def get(self, request, *args):
        geo_id = request.GET.get('geoId', None)
        boundary = request.GET.get('boundary', '')
        calculation = request.GET.get('calculation', 'household')
        supply_layer_id = request.GET.get(
            'supplyLayer',
            None
        )
        result = {}
        geography = Geography.objects.get(id=geo_id)

        if calculation == 'household':
            result = calculate_household(geography, boundary)
        elif calculation == 'urban':
            result = calculate_urban(geography, boundary)
        elif calculation == 'traditional':
            result = calculate_cooking_with_traditional(geography, boundary)
        elif calculation == 'poverty':
            result = calculate_poverty(geography, boundary)
        elif calculation == 'poverty-area' and supply_layer_id:
            supply_layer = Layer.objects.get(id=supply_layer_id)
            result = calculate_poverty_supply_layer_distance(
                geography, boundary, supply_layer)
        return Response(result)
