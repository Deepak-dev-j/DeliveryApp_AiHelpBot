from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.conf import settings


def index(request):
    """Serve the website (plain file read, so Django never touches the JS braces)."""
    html = (settings.BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    return HttpResponse(html)


urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api/", include("support.urls")),
]
