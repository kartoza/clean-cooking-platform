import os
import subprocess

from django.conf import settings


def simplify_layer(geonode_layer, output, tolerance=0.01):
    layer_created = False

    try:
        base_file = geonode_layer.layer.get_base_file()[0].file
    except IndexError:
        return layer_created

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
        '-sql',
        'SELECT ST_Union(geometry) AS geometry FROM {}'.format(layer_name),
        '-simplify',
        str(tolerance)])

    return os.path.exists(output)
