from django.shortcuts import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse


REDIRECT_TO = reverse('account_login')
EXEMPT_URLS = [ REDIRECT_TO, '' ]

class RestrictAccessMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and settings.RESTRICT_ACCESS:
            path = request.path_info.lstrip('/')
            if not any(m.lstrip('/') == path for m in EXEMPT_URLS):
                return HttpResponseRedirect(REDIRECT_TO)
        return self.get_response(request)
