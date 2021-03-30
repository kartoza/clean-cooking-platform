# coding=utf-8
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from custom.models.geography import Geography
from custom.serializers.geography_serializer import GeographySerializer


class GeographyDetail(APIView):

    def get(self, request, *args):
        name = self.request.GET.get('name', None)
        if name:
            geography = Geography.objects.get(
                name__iexact=name
            )
            return Response(
                GeographySerializer(geography, many=False).data
            )
        raise Http404
