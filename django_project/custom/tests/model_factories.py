import factory

from django.conf import settings
from django.utils import timezone

from geonode.layers.models import Layer, Style
from custom.models.dataset_file import DatasetFile


class UserF(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('id',)

    id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: "username%s" % n)
    first_name = factory.Sequence(lambda n: "first_name%s" % n)
    last_name = factory.Sequence(lambda n: "last_name%s" % n)
    email = factory.Sequence(lambda n: "email%s@example.com" % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_staff = False
    is_active = True
    is_superuser = False
    last_login = timezone.datetime(2000, 1, 1).replace(tzinfo=timezone.utc)
    date_joined = timezone.datetime(1999, 1, 1).replace(
        tzinfo=timezone.utc)

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserF, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class LayerF(factory.django.DjangoModelFactory):
    """
    Geonode layer
    """

    class Meta:
        model = Layer
        django_get_or_create = ('id', )

    id = factory.Sequence(lambda n: n)
    title = factory.Sequence(lambda n: 'Layer %s' % n)
    owner = factory.SubFactory(UserF)


class StyleF(factory.django.DjangoModelFactory):
    """
    Geonode style
    """

    class Meta:
        model = Style
        django_get_or_create = ('id', )

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Style %s' % n)


class DatasetFileF(factory.django.DjangoModelFactory):
    """
    CCA Dataset file factory
    """

    class Meta:
        model = DatasetFile

    label = factory.Sequence(lambda n: 'Dataset %s' % n)
    geonode_layer = factory.SubFactory(LayerF)
