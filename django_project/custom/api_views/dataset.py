# coding=utf-8
from django.http.response import Http404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from custom.models.category import Category
from custom.models.geography import Geography
from custom.serializers.dataset_serializer import (
    BoundaryGeographySerializer,
    DatasetSerializer
)
from custom.tools.category import category_from_url
from custom.utils.cache import get_cache_dataset, set_cache_dataset


class BoundariesDataset(APIView):

    def get(self, request, *args):
        geography_id = self.request.GET.get('geography', None)
        clipped_boundary = self.request.GET.get('boundary', None)
        try:
            geography = Geography.objects.get(
                id=geography_id
            )
        except Geography.DoesNotExist:
            raise Http404

        return Response(
            BoundaryGeographySerializer(geography, context={
                'clipped_boundary': clipped_boundary
            }).data
        )


class DatasetList(APIView):

    def get(self, request, *args):
        geography_id = self.request.GET.get('geography', None)
        clipped_boundary = self.request.GET.get('boundary', None)
        inputs = self.request.GET.get('inputs', None)

        dataset_key = f'{geography_id}{clipped_boundary}{inputs}'

        cached = get_cache_dataset(dataset_key)

        if inputs:
            inputs = inputs.split(',')

        if cached is None or not isinstance(cached, list):
            if inputs:
                datasets_from_inputs = category_from_url(inputs)
                dataset_id = []
                for dataset in datasets_from_inputs:
                    dataset_id.append(dataset['category'].id)
                datasets = Category.objects.filter(
                    id__in=dataset_id
                )
            else:
                datasets = Category.objects.all()
            datasets = datasets.filter(
                ~Q(datasetfile__endpoint='') |
                Q(datasetfile__geonode_layer__isnull=False),
                geography_id=geography_id,
                online=True
            ).exclude(
                boundary_layer=True,
            ).order_by('sidebar_sub_menu_obj__main_menu__order',
                       'sidebar_sub_menu_obj__order').distinct()

            cached = set_cache_dataset(dataset_key, DatasetSerializer(
                datasets, many=True, context={
                'clipped_boundary': clipped_boundary
            }).data)

        return Response(
            cached
        )


class DatasetDetail(APIView):

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, *args):
        pk = self.request.GET.get('id', None)
        name = self.request.GET.get('name', None)
        geography = self.request.GET.get('geography', None)
        layer = self.request.GET.get('layer', None)
        dataset = None
        filters = {}
        if name:
            filters = {
                'name_long__iexact': name
            }
        if layer:
            if layer == 'boundary' or layer == 'boundaries':
                filters = {
                    'boundary_layer': True
                }
        if geography:
            filters['geography_id'] = geography

        if filters:
            datasets = Category.objects.filter(
                **filters
            )
            if datasets.exists():
                dataset = datasets[0]
        if pk and not dataset:
            dataset = self.get_object(pk)

        if dataset:
            return Response(
                DatasetSerializer(dataset, many=False).data
            )

        raise Http404
