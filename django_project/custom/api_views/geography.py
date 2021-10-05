# coding=utf-8
import os.path
import uuid

from django.conf import settings
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from custom.models.geography import Geography
from custom.serializers.geography_serializer import GeographySerializer
from custom.tools.rasterize_layer import rasterize_layer


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


class GeographyRasterMask(APIView):

    def post(self, request, *args):
        geo_id = self.request.POST.get('geo_id', None)
        subregion_selector = self.request.POST.get('subregion_selector', None)
        subregion_value = self.request.POST.get('subregion_value', None)
        try:
            geo = Geography.objects.get(id=geo_id)
        except Geography.DoesNotExist:
            raise Http404

        shp_layer = (
            geo.vector_boundary_layer.upload_session.layerfile_set.filter(
                file__icontains='.shp').first()
        )
        shp_layer_file = shp_layer.file
        uuid_string = str(uuid.uuid3(
            uuid.NAMESPACE_OID,
            f'{shp_layer_file.path}{subregion_selector}{subregion_value}'
        )) + '.tif'

        raster_dir = os.path.join(settings.MEDIA_ROOT, 'rasterized')
        if not os.path.exists(raster_dir):
            os.mkdir(raster_dir)

        destination_path = os.path.join(
            raster_dir,
            uuid_string,
        )
        where_condition = f"{subregion_selector}='{subregion_value}'"

        if os.path.exists(shp_layer_file.path):
            try:
                rasterize_layer(
                    shp_layer_file.path,
                    0.05,
                    destination_path,
                    where_condition
                )
            except: # noqa
                raise Http404

        return Response({
            'Success': True,
            'Geo': geo.name,
            'Raster': f'{settings.MEDIA_URL}rasterized/{uuid_string}'
        })
