# This file It is for the app_version variable to be available in all templates.

from django.conf import settings

def app_version(request):
    return {
        "APP_VERSION": settings.APP_VERSION
    }
