from .utilities import get_default_filter_by_group
from django.conf import settings


def configs(request):
    """Global values to pass to templates"""

    defaults = dict(
        DEFAULT_GROUP_FILTER=get_default_filter_by_group(request.user),
        GEP_TITLE=settings.GEP_TITLE,
        GEP_SHORT_TITLE=settings.GEP_SHORT_TITLE,
        SDI_TITLE=settings.SDI_TITLE
    )

    return defaults
