from django.apps import AppConfig


class CustomConfig(AppConfig):
    name = 'custom'
    verbose_name = 'Clean Cooking Explorer'

    def ready(self):
        import custom.signals
