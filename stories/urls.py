from django.urls import path, include
from .views import (
    StationStoryView, 
    EpisodeCutListCreateView, 
    episode_detail_view, 
    toggle_bookmark
)
from . import views

urlpatterns = [
    # 1. HTML 렌더링 뷰 (기존 웹 페이지 유지)
    path('episode/<int:episode_id>/', views.episode_detail_view, name='episode_detail'),

    # 2. 역 식별자 기반 스토리 조회 API (팀원 추가 기능)
    path('station/<str:station_identifier>/', StationStoryView.as_view(), name='station-story'),

    # 3. 에피소드별 컷(Cuts) 관리 API (우리가 수정한 경로 유지)
    path("v1/episodes/<int:episode_id>/cuts/", EpisodeCutListCreateView.as_view(), name="episode_cuts"),

    # 4. 북마크 토글 기능 (팀원 추가 기능 - 나중에 API로 연동 가능)
    path('episode/<int:episode_id>/bookmark/', toggle_bookmark, name='toggle_bookmark'),

    # 5. 기타 내부 API 연결 (우리가 설정한 구조 유지)
    path('v1/lines/', include('pages.urls_api')),
    path('v1/stories/', include('stories.urls_api')),
]