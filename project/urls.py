# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.http import HttpResponse

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # health
    path("health/", health),

    # admin
    path("admin/", admin.site.urls),

    # --- API (React가 붙는 경로) ---
    path("api/accounts/", include("accounts.urls_api")),
    path("api/pages/", include("pages.urls_api")),
    path('api/stories/', include('stories.urls')),

    # --- HTML (Django 템플릿 쓰는 기존 화면) ---
    path("accounts/", include("accounts.urls")),
    path("stories/", include("stories.urls")),
    path("", include("pages.urls")),
    path('library/', include('library.urls')),
    
]

