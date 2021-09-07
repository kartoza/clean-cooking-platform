from geonode.people.adapters import LocalAccountAdapter
from django.urls import reverse


class CustomLocalAccountAdapter(LocalAccountAdapter):
    def get_login_redirect_url(self, request):
        home_path = reverse("home")
        return home_path
