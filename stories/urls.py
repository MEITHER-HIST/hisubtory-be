from django.urls import path, include
from stories.views import EpisodeCutListCreateView, episode_detail_view
from . import views

urlpatterns = [
    # 1. 브라우저 직접 접속용 HTML 렌더링 (기존 유지)
    # 주소 예시: /stories/episode/1/
    path('episode/<int:episode_id>/', views.episode_detail_view, name='episode_detail'),

    # 2. 에피소드별 컷(Cuts) 관리 API
    # 주소 예시: /stories/v1/episodes/1/cuts/
    path("v1/episodes/<int:episode_id>/cuts/", EpisodeCutListCreateView.as_view(), name="episode_cuts"),

    # 3. 기타 내부 API들 (기존 연결 유지)
    path('v1/lines/', include('pages.urls_api')),
    path('v1/stories/', include('stories.urls_api')),
]