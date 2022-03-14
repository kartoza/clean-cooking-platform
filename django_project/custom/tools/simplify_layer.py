import os
import subprocess

from django.conf import settings


def simplify_layer(geonode_layer, output, tolerance=0.05):

    try:
        base_file = geonode_layer.layer.get_base_file()[0].file
    except:  # noqa
        base_file = (
            geonode_layer.layer.upload_session.layerfile_set.all().filter(
                file__icontains='shp').first().file
        )

    if not base_file:
        return False

    layer_vector_file = os.path.join(
        settings.MEDIA_ROOT,
        base_file.name
    )

    # Check minified folder
    minified_folder = os.path.join(
        settings.MEDIA_ROOT,
        'minified'
    )

    if not os.path.exists(minified_folder):
        os.mkdir(minified_folder)

    if os.path.exists(output):
        os.remove(output)

    layer_name = os.path.basename(layer_vector_file).split('.')[0]

    subprocess.run([
        'ogr2ogr',
        '-f',
        'GeoJSON',
        '-overwrite',
        '-skipfailures',
        output,
        layer_vector_file,
        '-dialect',
        'sqlite',
        '-simplify',
        str(tolerance)])

    return os.path.exists(output)
