import base64

from django.core.files.base import ContentFile
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from geonode.layers.models import Layer
from custom.models import Preset, MapImage


@method_decorator(csrf_exempt, name='dispatch')
class MapImageApiView(APIView):

    def post(self, request, *args, **kwargs):
        boundary_uuid = request.data.get('boundaryUuid', '')
        image = request.data.get('image', None)
        preset = get_object_or_404(Preset, pk=request.data.get('presetId', -1))

        if not image or not boundary_uuid: raise Http404()

        img_format, img_str = image.split(';base64,')
        img_ext = img_format.split('/')[-1]
        img_data = ContentFile(
            base64.b64decode(img_str),
            name=f'{boundary_uuid}-{preset.id}.{img_ext}')

        # Get geonode layer
        geonode_layer_url = request.data.get('geonodeLayer', None)
        layer = None
        if geonode_layer_url:
            try:
                layer = Layer.objects.get(
                    name=geonode_layer_url.split('/')[-1].split('.')[0])
            except Layer.DoesNotExist:
                pass

        map_image, created = MapImage.objects.update_or_create(
            boundary_uuid=boundary_uuid,
            preset=preset,
            geonode_layer=layer,
            defaults={
                'image': img_data
            }
        )

        return Response({
            'status': 'created' if created else 'updated',
            'map_image_id': map_image.id
        })
