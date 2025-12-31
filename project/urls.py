from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# ✅ stories.views에서 명시적으로 가져옵니다. 
# 만약 stories/views.py에 이 클래스가 없다면 에러가 날 것이므로 확인이 필요합니다.
from stories.views import EpisodeDetailAPIView

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # 1. 시스템 관련
    path("health/", health),
    path("admin/", admin.site.urls),

    # 2. API 전용 경로
    # ✅ NameError를 방지하기 위해 import한 클래스를 직접 사용합니다.
    path("api/pages/v1/episode/detail/", 
         EpisodeDetailAPIView.as_view(), 
         name="episode_detail_api"),
    
    path("api/accounts/", include("accounts.urls_api")),
    path("api/pages/", include("pages.urls_api")),
    path("api/stories/", include("stories.urls")),
    path("api/library/", include("library.urls")),

    # 3. HTML/Legacy 경로
    path("accounts/", include("accounts.urls")),
    path("stories/", include("stories.urls")),
    path("library/", include("library.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)