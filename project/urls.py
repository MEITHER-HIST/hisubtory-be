from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# health 체크용
def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # health 체크
    path("health/", health),

    # admin
    path('admin/', admin.site.urls),

    # accounts 앱
    path('accounts/', include('accounts.urls')),         # HTML
    path('accounts/api/', include('accounts.urls_api')), # API

    # stories 앱
    path('stories/', include('stories.urls')),          # HTML
    path('stories/api/', include('stories.urls_api')),   # API

    # pages 앱
    path('', include('pages.urls')),                    # HTML
    path('pages/api/', include('pages.urls_api')),      # API
]

# static, media 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 