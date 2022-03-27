import os
import urllib.parse

import requests
from django.conf import settings
from django.db.models import Q
from django.contrib.sites.models import Site
from rest_framework import serializers
from slugify import slugify
from custom.models.category import Category
from custom.models.geography import Geography
from custom.models.dataset_file import DatasetFile, VECTORS
from custom.models.clipped_layer import ClippedLayer
from geonode.base.models import Link

from custom.tools.simplify_layer import simplify_layer


def geonode_layer_links(geonode_layer, geography):
    """
    Return links for layer and the style
    """
    if geonode_layer.is_vector():
        file_type = 'geojson'
    else:
        file_type = 'geotiff'
    links = Link.objects.filter(
        resource=geonode_layer,
        name__iexact=file_type
    )
    layer_url = None
    if links.exists():
        url = links[0].url
        url = urllib.parse.unquote(url)
        url = url.replace('EPSG:3857', 'EPSG:4326')
        x = geography.boundary_dimension_x
        y = geography.boundary_dimension_y
        current_site = Site.objects.get_current()
        layer_url = '{url}&SCALESIZE=i({x}),j({y})'.format(
            url=url,
            x=x,
            y=y
        )
        if current_site.domain not in layer_url:
            layer_url = '/proxy_cca/' + layer_url

    try:
        style_url = geonode_layer.default_style.sld_url
    except AttributeError:
        style_url = ''

    if not style_url:
        default_styles_geoserver = None
        try:
            url = (
                f'{settings.GEOSERVER_PUBLIC_LOCATION}/'
                f'rest/workspaces/geonode/styles.json'
            )
            r = requests.get(url)
            if r.status_code == 200:
                default_styles_geoserver = (
                    r.json()['styles']['style']
                )
        except KeyError:
            pass

        if default_styles_geoserver:
            for default_style in default_styles_geoserver:
                if default_style['name'] == geonode_layer.name:
                    style_url = default_style['href'].replace(
                        '.json', '.sld'
                    )

    current_site = Site.objects.get_current()
    if 'example' not in current_site.domain:
        style_url = style_url.replace(
            settings.GEOSERVER_LOCATION,
            'http://{}/geoserver/'.format(current_site.domain)
        )
    if current_site.domain not in style_url:
        style_url = '/proxy_cca/' + style_url
    return layer_url, style_url


class BoundaryGeographySerializer(serializers.ModelSerializer):
    name_long = serializers.SerializerMethodField()
    df = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return 'boundaries'

    def get_category(self, obj):
        return {
            'vectors': {
                "opacity": 1,
                "shape_type": "polygons",
            },
            'raster': {
                "init": None,
                "scale": None,
                "domain": None,
                "intervals": None,
                "precision": 0
            }
        }

    def get_df(self, obj):
        dataset_files = []
        clipped_boundary = self.context.get('clipped_boundary', None)
        use_clipped_boundary = False
        if clipped_boundary:
            clipped_boundary_file = os.path.join(
                settings.MEDIA_ROOT, 'rasterized', clipped_boundary + '.tif')
            if os.path.exists(clipped_boundary_file):
                use_clipped_boundary = True
        if obj.raster_mask_layer:
            layer_url, style_url = geonode_layer_links(
                obj.raster_mask_layer,
                obj
            )
            if use_clipped_boundary:
                layer_url = f'{settings.MEDIA_URL}rasterized/{clipped_boundary}.tif'
            dataset_files.append({
                'func': 'raster',
                'active': True,
                'file': {
                    'endpoint': '-',
                    'geonode_layer': layer_url if layer_url else '-',
                    'style': style_url or ''
                },
            })
        if obj.vector_boundary_layer:
            layer_url, style_url = geonode_layer_links(
                obj.vector_boundary_layer,
                obj
            )
            if use_clipped_boundary:
                layer_url = f'{settings.MEDIA_URL}rasterized/{clipped_boundary}.json'
            else:
                # Merge and simplify layer
                simplified_layer = os.path.join(
                    settings.MEDIA_ROOT,
                    'minified',
                    f'{obj.vector_boundary_layer.name}.json'
                )
                if not os.path.exists(simplified_layer):
                    simplify_layer(
                        obj.vector_boundary_layer,
                        simplified_layer
                    )
                if os.path.exists(simplified_layer):
                    layer_url = (
                        f'{settings.MEDIA_URL}minified/'
                        f'{obj.vector_boundary_layer.name}.json'
                    )

            dataset_files.append({
                'func': 'vectors',
                'active': True,
                'file': {
                    'endpoint': '-',
                    'geonode_layer': layer_url if layer_url else '-',
                    'style': style_url or ''
                },
            })
        return dataset_files

    def get_name_long(self, obj):
        return 'Administrative Boundaries'

    class Meta:
        model = Geography
        fields = ['name', 'name_long', 'online', 'category', 'df']



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DatasetFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        geonode_layer = None
        style = None
        clipped_boundary = self.context.get('clipped_boundary', None)
        layer_file = None

        if clipped_boundary:
            clipped_layer = ClippedLayer.objects.filter(
                layer=obj.geonode_layer,
                boundary_uuid=clipped_boundary).first()
            if clipped_layer and clipped_layer.clipped_file:
                layer_file = clipped_layer.clipped_file.url
            else:
                clipped_layer_directory = os.path.join(
                    settings.MEDIA_ROOT,
                    'clipped_layers',
                    f'{obj.geonode_layer.typename}:{clipped_boundary}'
                )
                if os.path.exists(clipped_layer_directory):
                    for clipped_file in os.listdir(clipped_layer_directory):
                        if '.json' or '.tif' in clipped_file:
                            layer_file = os.path.join(
                                clipped_layer_directory,
                                clipped_file
                            )
                            if os.path.exists(layer_file):
                                layer_file = (
                                    layer_file.replace(
                                        settings.MEDIA_ROOT,
                                        settings.MEDIA_URL)
                                )
                            else:
                                layer_file = None
                                geonode_layer = None
        if obj.use_geonode_layer and obj.geonode_layer:
            geonode_layer, style = geonode_layer_links(
                obj.geonode_layer,
                obj.category.geography
            )
        if layer_file:
            geonode_layer = layer_file
        return {
            'id': obj.id,
            'endpoint': obj.endpoint.url if obj.endpoint else '-',
            'configuration': obj.configuration,
            'geonode_layer': geonode_layer if geonode_layer else '-',
            'style': style or '',
            'comment': obj.comment
        }

    class Meta:
        model = DatasetFile
        fields = ['func', 'active', 'file']


class DatasetSerializer(serializers.ModelSerializer):

    df = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    geonode_metadata = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    def get_df(self, obj):
        return DatasetFileSerializer(
            obj.datasetfile_set.filter(
                ~Q(endpoint='') | Q(geonode_layer__isnull=False)
            ),
            many=True,
            context={
                'clipped_boundary': self.context.get('clipped_boundary', None)
            }
        ).data

    def get_unit(self, obj):
        if obj.unit_object:
            return obj.unit_object.name
        return ''

    def get_name(self, obj):
        if obj.boundary_layer:
            return 'boundaries'
        return slugify(obj.name_long)

    def get_custom_controls(self, obj):
        controls = {}
        path = ['', '']
        if not obj.boundary_layer:
            if obj.sidebar_sub_menu_obj:
                path = [
                    slugify(obj.sidebar_sub_menu_obj.main_menu.name),
                    slugify(obj.sidebar_sub_menu_obj.name)
                ]
        controls['range_label'] = self.get_unit(obj)
        controls['path'] = path
        controls['weight'] = obj.weight
        controls['range_steps'] = obj.legend_range_steps
        controls['range'] = obj.range_type
        return controls

    def get_geonode_metadata(self, obj):
        dataset_files = DatasetFile.objects.filter(
            category_id=obj.id,
            use_geonode_layer=True,
            geonode_layer__isnull=False
        )
        if dataset_files.exists():
            dataset_file = None
            if dataset_files.count() > 1:
                dataset_file = dataset_files.filter(
                    func=VECTORS
                ).first()
            if not dataset_file:
                dataset_file = dataset_files.first()
            return '/api/v2/layers/{}/'.format(
                dataset_file.geonode_layer.id
            )
        return '-'

    def _get_analysis(self, obj):
        _analysis = obj.analysis
        _analysis['indexes'] = []
        if obj.eap_use:
            _analysis['indexes'].append({
                'index': 'eai',
                'scale': obj.eap_scale,
                'invert': obj.eap_invert
            })
        if obj.demand_index:
            _analysis['indexes'].append({
                'index': 'demand',
                'scale': obj.demand_scale,
                'invert': obj.demand_invert
            })
        if obj.supply_index:
            _analysis['indexes'].append({
                'index': 'supply',
                'scale': obj.supply_scale,
                'invert': obj.supply_invert
            })
        if obj.ani_index:
            _analysis['indexes'].append({
                'index': 'ani',
                'scale': obj.ani_scale,
                'invert': obj.ani_invert
            })
        return _analysis

    def get_category(self, obj):
        return {
            'domain': obj.domain,
            'domain_init': obj.domain_init,
            'colorstops': obj.colorstops,
            'raster': obj.raster,
            'vectors': obj.vectors,
            'csv': obj.csv,
            'analysis': self._get_analysis(obj),
            'timeline': obj.timeline,
            'controls': self.get_custom_controls(obj)
        }

    class Meta:
        model = Category
        fields = [
            'name',
            'name_long',
            'unit',
            'pack',
            'circle',
            'online',
            'metadata',
            'geonode_metadata',
            'category',
            'df'
        ]
