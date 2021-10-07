import os
import subprocess


def clip_vector_layer(
        layer_vector_file = '',
        boundary_layer_file = '',
        output_path = ''):

    if os.path.exists(output_path):
        basename = os.path.basename(output_path)
        basename = basename.replace('.shp', '')
        for file_name in os.listdir(os.path.dirname(output_path)):
            if basename in file_name:
                os.remove(os.path.join(os.path.dirname(output_path), file_name))

    subprocess.run([
        'ogr2ogr',
        '-clipsrc',
        boundary_layer_file,
        output_path,
        layer_vector_file])
