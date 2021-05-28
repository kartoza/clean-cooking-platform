from django.contrib import admin
from django.contrib.postgres import fields
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget
from preferences.admin import PreferencesAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models.geography import Geography
from .models.category import Category
from .models.dataset_file import DatasetFile
from .models.cca_preference import CCAPreferences
from .models.unit import Unit
from .models.menu import *


class MapSlugMappingAdmin(admin.ModelAdmin):
    list_display = ('map', 'slug')


class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ['name', ]


class GeographyAdmin(admin.ModelAdmin):
    list_display = ('name', 'cca3', 'created_at', 'updated')
    exclude = ('configuration', 'circle', 'pack', 'parent', 'adm')
    search_fields = ('name', )
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


class DatasetFileInline(admin.StackedInline):
    model = DatasetFile
    autocomplete_fields = ['geonode_layer', ]
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    extra = 0

    class Media:
        js = ('/static/admin/js/show_geonode_layer.js', )


class DatasetFileAdmin(admin.ModelAdmin):
    list_display = (
        'category', 'label', 'func', 'geonode_layer', 'active'
    )


class MainMenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    autocomplete_fields = ['geography', ]
    search_fields = ('name', )
    list_display = ('name', 'geography')


class SubMenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    autocomplete_fields = ['main_menu', ]
    search_fields = ('name', 'main_menu__name')
    list_display = ('name', 'main_menu')


class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'name_long', 'sidebar_sub_menu_obj', 'dataset', 'online')

    autocomplete_fields = ['unit_object', 'sidebar_sub_menu_obj' ]

    list_display_links = ('name_long', )

    list_filter = (
        'online',
        'sidebar_sub_menu_obj'
    )

    fieldsets = (
        (None, {
            'fields': ('geography', 'name_long', 'unit_object', 'online', 'sidebar_sub_menu_obj', 'legend_range_steps')
        }),
        ('Advanced configurations', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('boundary_layer', 'analysis', 'controls', 'configuration', 'domain', 'domain_init', 'timeline', 'vectors', 'metadata'),
        }),
    )

    def dataset(self, obj):
        html = ''
        for dataset_file in obj.datasetfile_set.all():
            dataset_found = False
            if dataset_file.use_geonode_layer and dataset_file.geonode_layer:
                html += '<a href={} target="_blank"> <span class="badge badge-secondary">Layer</span> '.format(
                    dataset_file.geonode_layer.detail_url
                )
                dataset_found = True
            elif dataset_file.endpoint:
                html += '<a href={}>'.format(
                    dataset_file.endpoint.url
                )
                dataset_found = True
            if dataset_found:
                if dataset_file.label:
                    html += dataset_file.label
                else:
                    html += '{} file'.format(dataset_file.func)
                html += '</a>'
            else:
                html += '-'
            html += '<br>'
        return format_html(html)

    dataset.short_description = 'Dataset'
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget(height='250px')},
    }
    inlines = [
        DatasetFileInline
    ]


admin.site.register(Geography, GeographyAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(DatasetFile, DatasetFileAdmin)
admin.site.register(CCAPreferences, PreferencesAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(SubMenu, SubMenuAdmin)
