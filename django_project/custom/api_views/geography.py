# coding=utf-8
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from custom.models.geography import Geography
from custom.serializers.geography_serializer import GeographySerializer


class GeographyDetail(APIView):

    def get(self, request, *args):
        name = self.request.GET.get('name', None)
        geo = self.request.GET.get('geo', None)
        filters = {}
        if name:
            filters = {
                'name__iexact': name
            }
        if geo:
            filters = {
                'id': geo
            }
        if filters:
            geography = Geography.objects.get(
                **filters
            )
            return Response(
                GeographySerializer(geography, many=False).data
            )
        raise Http404


class GeographyList(APIView):

    def get(self, request, *args):
        geo = self.request.GET.get('geo', None)
        additional_filters = {}
        if geo:
            additional_filters = {
                'id': geo,
                'parent__id': geo
            }
        return Response(
            GeographySerializer(Geography.objects.filter(
                online=True,
                **additional_filters
            ), many=True).data
        )
