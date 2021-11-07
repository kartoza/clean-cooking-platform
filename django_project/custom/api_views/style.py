import os

import requests
from wsgiref.util import FileWrapper

from django.http.response import HttpResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.core.cache import cache

from core.settings.utils import absolute_path


class StyleApiView(APIView):

    sld_file = absolute_path(
       'custom',
       'static/geonode__bytetest.sld')

    def post(self, request, *args, **kwargs):
        dataset_id = request.data.get('datasetId', '')
        style_data = request.data.get('styleData', '')

        cache.set('style_dataset_{}'.format(dataset_id), style_data)
        return Response('Updated')

    def get(self, request, *args):
        dataset_id = request.GET.get('datasetId', '')
        style_url = request.GET.get('styleUrl', '')
        style_url = style_url.replace('/proxy_cca/', '')
        style_name = style_url.split('/')[-1]

        if not dataset_id or not style_url or not style_name:
            raise Http404()

        cached_style = cache.get('style_dataset_{}'.format(dataset_id))

        if cached_style:
            return Response(cached_style)

        # Check if style already download in media file
        styles_folder = os.path.join(settings.MEDIA_ROOT, 'styles')
        if not os.path.exists(styles_folder):
            os.mkdir(styles_folder)

        dataset_style_folder = os.path.join(styles_folder, dataset_id)
        if not os.path.exists(dataset_style_folder):
            os.mkdir(dataset_style_folder)

        style_file = os.path.join(
            dataset_style_folder,
            style_name
        )

        if not os.path.exists(style_file):
            r = requests.get(url=style_url, stream=True)
            chunk_size = 2000
            with open(style_file, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)

        return HttpResponse(open(style_file).read(),
                            content_type='text/xml')
