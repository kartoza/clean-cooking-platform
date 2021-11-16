import copy
from geonode.settings import *
from .utils import absolute_path  # noqa

INSTALLED_APPS += (
    'django_json_widget',
    'preferences',
    'adminsortable2',
    'custom',
)

INSTALLED_APPS = (
    'grappelli.dashboard',
    'filebrowser',
    'django_cleanup.apps.CleanupConfig',
) + INSTALLED_APPS

MIDDLEWARE = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'dj_pagination.middleware.PaginationMiddleware',
    # The setting below makes it possible to serve different languages per
    # user depending on things like headers in HTTP requests.
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'geonode.base.middleware.MaintenanceMiddleware',
    'geonode.base.middleware.ReadOnlyMiddleware',  # a Middleware enabling Read Only mode of Geonode
    # 'custom.middlewares.access_middleware.RestrictAccessMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
TEMPLATES = [
    {
        'NAME': 'GeoNode Project Templates',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                'geonode.context_processors.resource_urls',
                'geonode.geoserver.context_processors.geoserver_urls',
                'geonode.themes.context_processors.custom_theme',

                # custom context processor
                'custom.context_processors.configs',
                'preferences.context_processors.preferences_cp',
            ],
            'debug': DEBUG,
        },
    },
]

_DEFAULT_LANGUAGES = (
    # ('id', 'Bahasa Indonesia'),
    ('en', 'English'),
    ('fr', 'Français'),
)
LANGUAGES = os.getenv('LANGUAGES', _DEFAULT_LANGUAGES)

# Additional locations of static files
STATICFILES_DIRS = [absolute_path('custom', 'static'), ] + STATICFILES_DIRS

# Additional locations of templates
TEMPLATES[0]['DIRS'] = [absolute_path('custom', 'templates')] + TEMPLATES[0]['DIRS']

# Wagtail Settings
WAGTAIL_SITE_NAME = 'My Example Site'
WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS = True
# -- END Settings for Wagtail

ROOT_URLCONF = 'core.urls'
LOCALE_PATHS += (
    os.path.join(PROJECT_ROOT, 'custom', 'locale'),
)

GEP_TITLE = os.getenv('GEP_TITLE', 'Global Electrification Programme')
GEP_SHORT_TITLE = os.getenv('GEP_SHORT_TITLE', 'BEP')
SDI_TITLE = os.getenv('SDI_TITLE', 'Global Electrification Platform SDI')
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', '')
MAPBOX_THEME = os.getenv('MAPBOX_THEME', '')

GRAPPELLI_INDEX_DASHBOARD = 'custom.dashboard.CustomIndexDashboard'
FILEBROWSER_DIRECTORY = ''
DIRECTORY = ''

RESTRICT_ACCESS = ast.literal_eval(os.getenv('RESTRICT_ACCESS', 'False'))
ACCOUNT_ADAPTER = 'custom.adapters.CustomLocalAccountAdapter'
STATICFILES_STORAGE = 'core.storage.WhiteNoiseStaticFilesStorage'

CELERY_TASK_ALWAYS_EAGER = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'cache:11211',
    }
}

PROXY_ALLOWED_HOSTS += ['geoserver']
