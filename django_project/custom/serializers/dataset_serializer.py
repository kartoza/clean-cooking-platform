from rest_framework import serializers
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
                x = preferences.CCAPreferences.boundary_dimension_x
                y = preferences.CCAPreferences.boundary_dimension_y
                geonode_layer = '/proxy_cca/{url}&SCALESIZE=i({x}),j({y})'.format(
                    url=links[0].url,
                    x=x,
                    y=y
                )
            style = '/proxy_cca/' + obj.geonode_layer.default_style.sld_url
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

    df = DatasetFileSerializer(
        source='datasetfile_set',
        many=True
    )
    category = serializers.SerializerMethodField()
    geonode_metadata = serializers.SerializerMethodField()

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

    def get_category(self, obj):
        return {
            'domain': obj.domain,
            'domain_init': obj.domain_init,
            'colorstops': obj.colorstops,
            'raster': obj.raster,
            'vectors': obj.vectors,
            'csv': obj.csv,
            'analysis': obj.analysis,
            'timeline': obj.timeline,
            'controls': obj.controls
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
