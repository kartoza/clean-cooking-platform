# coding=utf-8
import json
from django.http.response import HttpResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from custom.models.dataset import Dataset
from custom.serializers.dataset_serializer import DatasetSerializer


class DatasetList(APIView):

    def get(self, request, *args):
        geography_id = self.request.GET.get('geography', None)
        datasets = Dataset.objects.filter(
            geography_id=geography_id
        ).exclude(
            category__name__iexact='boundaries'
        )
        return Response(
            DatasetSerializer(datasets, many=True).data
        )


class DatasetDetail(APIView):

    def get_object(self, pk):
        try:
            return Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist:
            raise Http404

    def get(self, request, *args):
        pk = self.request.GET.get('id', None)
        name = self.request.GET.get('name', None)
        geography = self.request.GET.get('geography', None)
        dataset = None
        filters = {}
        if name:
            filters = {
                'name__iexact': name
            }
        if geography:
            filters['geography_id'] = geography

        if filters:
            datasets = Dataset.objects.filter(
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
