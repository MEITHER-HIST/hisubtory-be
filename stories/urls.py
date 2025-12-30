from django.urls import path
from .views import (
    StationStoryView, 
    EpisodeCutListCreateView, 
    episode_detail_view, 
    toggle_bookmark
)

urlpatterns = [
    # 1. HTML 렌더링 뷰 (웹 페이지용)
    # 호출: /stories/episode/1/
    path('episode/<int:episode_id>/', episode_detail_view, name='episode_detail'),

    # 2. 역 식별자(이름 또는 ID) 기반 스토리 조회 API (React 메인용)
    # 호출: /stories/station/종로3가/ 또는 /stories/station/1/
    path('station/<str:station_identifier>/', StationStoryView.as_view(), name='station-story'),

    # 3. 에피소드별 컷 리스트 API (관리자용)
    # 호출: /stories/episodes/1/cuts/
    path('episodes/<int:episode_id>/cuts/', EpisodeCutListCreateView.as_view(), name='episode_cuts'),

    # 4. 북마크 토글 기능 (웹용)
    # 호출: /stories/episode/1/bookmark/
    path('episode/<int:episode_id>/bookmark/', toggle_bookmark, name='toggle_bookmark'),
]