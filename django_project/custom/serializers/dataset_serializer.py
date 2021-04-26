from rest_framework import serializers
from custom.models.dataset import Dataset
from custom.models.category import Category
from custom.models.dataset_file import DatasetFile
from geonode.base.models import Link
from geonode.layers.models import Style


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
                geonode_layer = '/proxy_cca/' + links[0].url + '&SCALESIZE=i(604),j(636)'
            style = '/proxy_cca/' + obj.geonode_layer.default_style.sld_url
        return {
            'id': obj.id,
            'endpoint': obj.endpoint.url,
            'configuration': obj.configuration,
            'geonode_layer': geonode_layer if geonode_layer else '-',
            'test': obj.test,
            'style': style if style else '-',
            'comment': obj.comment,
            'created': obj.created_at,
            'created_by': obj.created_by.id if obj.created_by else None,
            'updated': obj.updated,
            'updated_by': obj.updated_by.id if obj.updated_by else None
        }

    class Meta:
        model = DatasetFile
        fields = ['id', 'dataset_id', 'func', 'active', 'file']


class DatasetSerializer(serializers.ModelSerializer):

    category = CategorySerializer('category', many=False)
    df = DatasetFileSerializer(
        source='datasetfile_set',
        many=True
    )

    class Meta:
        model = Dataset
        fields = '__all__'
