from rest_framework import serializers
from custom.models.dataset import Dataset
from custom.models.category import Category
from custom.models.dataset_file import DatasetFile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DatasetFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        geonode_layer = None
        if obj.use_geonode_layer and obj.geonode_layer:
            geonode_layer = obj.geonode_layer
        return {
            'id': obj.id,
            'endpoint': obj.endpoint.url,
            'configuration': obj.configuration,
            'geonode_layer': geonode_layer.name if geonode_layer else '-',
            'test': obj.test,
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
