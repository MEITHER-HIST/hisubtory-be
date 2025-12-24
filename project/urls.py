from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("health/", views.health),

    # admin
    path('admin/', admin.site.urls),

    # HTML
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    path('stories/', include('stories.urls')),

    # API
    path('api/accounts/', include('accounts.urls_api')),
    path('api/', include('pages.urls_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
