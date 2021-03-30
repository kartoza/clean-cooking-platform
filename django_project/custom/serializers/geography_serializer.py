import json
from rest_framework import serializers
from custom.models.geography import Geography


class GeographySerializer(serializers.ModelSerializer):

    class Meta:
        model = Geography
        fields = '__all__'

