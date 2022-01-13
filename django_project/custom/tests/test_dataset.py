from unittest.mock import patch
import os

from django.test import TestCase
from django.core.cache import cache
from custom.tests.model_factories import *


class TestDataset(TestCase):

    def setUp(self):
        self.style = StyleF.create()
        self.layer = LayerF.create(
            default_style=self.style
        )
        self.dataset_file = DatasetFileF.create(
            geonode_layer=self.layer
        )

    @patch('custom.models.dataset_file.remove_dataset_cache')
    def test_signal_handler_called(self, mock):
        self.layer.save()
        mock.assert_called_once_with(self.dataset_file, self.layer)

    def test_delete_cache_on_post_save(self):
        style_dataset_key = f'style_dataset_{self.dataset_file.id}'
        cache.set(style_dataset_key, {
            'style': 'data'
        })

        styles_folder = os.path.join(settings.MEDIA_ROOT, 'styles')
        if not os.path.exists(styles_folder):
            os.mkdir(styles_folder)
        dataset_style_folder = os.path.join(
            styles_folder, str(self.dataset_file.id))
        os.mkdir(dataset_style_folder)
        style_file = os.path.join(dataset_style_folder, 'styles.sld')
        open(style_file, 'a').close()

        self.assertIsNotNone(cache.get(style_dataset_key.format(
            self.dataset_file.id
        )))
        self.assertTrue(os.path.exists(style_file))
        self.style.save()
        self.assertIsNone(cache.get(style_dataset_key.format(
            self.dataset_file.id
        )))
        self.assertFalse(os.path.exists(style_file))
