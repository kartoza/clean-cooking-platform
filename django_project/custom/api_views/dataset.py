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


class BoundariesDataset(APIView):

    def get(self, request, *args):
        geography_id = self.request.GET.get('geography', None)
        try:
            geography = Geography.objects.get(
                id=geography_id
            )
        except Geography.DoesNotExist:
            raise Http404

        return Response(
            BoundaryGeographySerializer(geography).data
        )


class DatasetList(APIView):

    def get(self, request, *args):
        geography_id = self.request.GET.get('geography', None)
        datasets = Category.objects.filter(
            ~Q(datasetfile__endpoint='') |
            Q(datasetfile__geonode_layer__isnull=False),
            geography_id=geography_id,
            online=True
        ).exclude(
            boundary_layer=True,
        ).distinct()
        return Response(
            DatasetSerializer(datasets, many=True).data
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
