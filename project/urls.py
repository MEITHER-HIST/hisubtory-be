from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# stories.views에서 필요한 API 뷰들을 가져옵니다.
# 만약 이 줄에서 에러가 난다면 stories/views.py에 해당 클래스가 있는지 확인해야 합니다.
try:
    from stories.views import EpisodeDetailAPIView, EpisodeCutListCreateView
except ImportError:
    # 혹시라도 파일이 꼬여서 못 가져올 경우를 대비한 방어 코드
    EpisodeDetailAPIView = None
    EpisodeCutListCreateView = None

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # 1. Health & Admin
    path("health/", health),
    path("admin/", admin.site.urls),

    # 2. API (React 요청 경로)
    # EpisodeDetailAPIView가 정상적으로 import 되었을 때만 경로를 활성화합니다.
    path("api/pages/v1/episode/detail/", 
         EpisodeDetailAPIView.as_view() if EpisodeDetailAPIView else health, 
         name="episode_detail_api"),
    
    path("api/accounts/", include("accounts.urls_api")),
    path("api/pages/", include("pages.urls_api")),
    path('api/stories/', include('stories.urls')),

    # 3. HTML & Legacy URLs
    path("accounts/", include("accounts.urls")),
    path("stories/", include("stories.urls")),
    path("", include("pages.urls")),
    path('library/', include('library.urls')),
]

# 미디어 파일 설정 (S3를 쓰더라도 로컬 개발 환경을 위해 유지)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)