# project/urls.py 전문

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# 중요: 에러 방지를 위해 직접 import
from stories.views import EpisodeDetailAPIView, EpisodeCutListCreateView

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # 1. Health & Admin
    path("health/", health),
    path("admin/", admin.site.urls),

    # 2. API (React 요청 경로)
    # 프론트엔드가 찾는 그 주소 그대로 연결합니다.
    path("api/pages/v1/episode/detail/", EpisodeDetailAPIView.as_view(), name="episode_detail_api"),
    path("api/accounts/", include("accounts.urls_api")),
    path("api/pages/", include("pages.urls_api")),
    path('api/stories/', include('stories.urls')),

    # 3. HTML & Legacy URLs
    path("accounts/", include("accounts.urls")),
    path("stories/", include("stories.urls")),
    path("", include("pages.urls")),
    path('library/', include('library.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)