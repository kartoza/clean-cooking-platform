"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'django_project.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        self.children.append(modules.Group(
            _('Clean Cooking Explorer'),
            column=1,
            collapsible=False,
            children = [
                modules.ModelList(
                    _(''),
                    column=1,
                    collapsible=False,
                    models=(
                        'custom.models.geography.Geography',
                        'custom.models.category.Category',
                        'custom.models.unit.Unit',
                        'custom.models.menu.MainMenu',
                        'custom.models.menu.SubMenu',)
                )
            ]
        ))

        # append a group for "Administration"
        self.children.append(modules.Group(
            _('Group: Administration'),
            column=1,
            collapsible=True,
            css_classes=['grp-closed'],
            children = [
                modules.AppList(
                    _('Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*',),
                )
            ]
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('GeoNode'),
            collapsible=True,
            column=1,
            css_classes=['grp-closed'],
            exclude=('django.contrib.*', 'custom.*'),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('ModelList: Administration'),
            column=1,
            collapsible=True,
            css_classes=['grp-closed'],
            models=('django.contrib.*',),
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media Management'),
            column=2,
            children=[
                {
                    'title': _('FileBrowser'),
                    'url': '/admin/filebrowser/browse/',
                    'external': False,
                },
            ]
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))
