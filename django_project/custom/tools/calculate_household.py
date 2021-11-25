import time

from django.conf import settings

from custom.models import ClippedLayer
from custom.models.geography import Geography
from custom.tasks import clip_layer_by_region


def calculate_household(geography: Geography, boundary_id: str):
    import rasterio
    import geopandas as gpd

    if not geography:
        return None

    if not geography.household_layer:
        return None

    start_time = time.time()

    if boundary_id:
        clipped_layer, created = ClippedLayer.objects.get_or_create(
            layer=geography.household_layer,
            boundary_uuid=boundary_id
        )
        if created or not clipped_layer.clipped_file:
            clipped_layer = clip_layer_by_region(
                clipped_layer.id
            )
        vector_file = settings.MEDIA_ROOT + str(clipped_layer.clipped_file)
    else:
        try:
            base_file = geography.household_layer.get_base_file()[0].file
        except:  # noqa
            base_file = (
                geography.household_layer.upload_session.layerfile_set.all(
                ).filter(
                    file__icontains='shp'
                ).first().file
            )
        vector_file = base_file.path
    features = gpd.read_file(vector_file)
    total_household = features.sum()[geography.household_layer_field]

    return {
        'layer': vector_file,
        'execution_time': time.time() - start_time,
        'total_household': total_household
    }
