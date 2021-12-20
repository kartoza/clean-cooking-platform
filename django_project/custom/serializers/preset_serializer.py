from urllib.parse import urlparse
from urllib.parse import parse_qs
from rest_framework import serializers
from custom.models.preset import Preset
from custom.models.category import Category


class PresetSerializer(serializers.ModelSerializer):
    layers = serializers.SerializerMethodField()
    analysis = serializers.SerializerMethodField()

    def get_analysis(self, obj):
        return ','.join(
            obj.summaryreportcategory_set.values_list(
                'analysis',
                flat=True).distinct()
        )

    def get_layers(self, obj):
        permalink = obj.permalink
        parsed_url = urlparse(permalink)
        layer_inputs = parse_qs(parsed_url.query)['inputs'][0].split(',')
        layer_ids = []
        for layer_input in layer_inputs:
            layer_input = layer_input.replace('-', ' ')
            category = Category.objects.filter(
                name_long__icontains=layer_input).first()
            if category:
                for dataset in category.datasetfile_set.filter(
                        geonode_layer__isnull=False):
                    layer_ids.append(dataset.geonode_layer.id)
        return layer_ids

    class Meta:
        model = Preset
        fields = ['id', 'name', 'description', 'layers', 'permalink',
                  'analysis']

