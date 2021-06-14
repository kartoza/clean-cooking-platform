from django.conf import settings
from django.db.models import Q
from django.contrib.sites.models import Site
from rest_framework import serializers
from slugify import slugify
from preferences import preferences
from custom.models.category import Category
from custom.models.dataset_file import DatasetFile
from geonode.base.models import Link


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DatasetFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        geonode_layer = None
        style = None
        if obj.use_geonode_layer and obj.geonode_layer:
            if obj.func == 'raster':
                file_type = 'geotiff'
            else:
                file_type = 'geojson'
            links = Link.objects.filter(
                resource = obj.geonode_layer,
                name__iexact= file_type
            )
            if links.exists():
                x = obj.category.geography.boundary_dimension_x
                y = obj.category.geography.boundary_dimension_y
                geonode_layer = '/proxy_cca/{url}&SCALESIZE=i({x}),j({y})'.format(
                    url=links[0].url,
                    x=x,
                    y=y
                )
            style_url = obj.geonode_layer.default_style.sld_url
            current_site = Site.objects.get_current()
            if 'example' not in current_site.domain:
                style_url = style_url.replace(
                    settings.GEOSERVER_LOCATION,
                    'http://{}/geoserver/'.format(current_site.domain)
                )
            style = '/proxy_cca/' + style_url
        return {
            'id': obj.id,
            'endpoint': obj.endpoint.url if obj.endpoint else '-',
            'configuration': obj.configuration,
            'geonode_layer': geonode_layer if geonode_layer else '-',
            'style': style if style else '-',
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
            many=True
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
            dataset_file = dataset_files[0]
            return '/catalogue/csw_to_extra_format/{}/metadata.html'.format(
                dataset_file.geonode_layer.uuid
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
            'configuration',
            'metadata',
            'geonode_metadata',
            'category',
            'df'
        ]
