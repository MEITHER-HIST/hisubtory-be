from django.urls import path
from . import views
from .views import (
    StationStoryView, 
    EpisodeCutListCreateView, 
    WebtoonListView,
    EpisodeDetailAPIView,
    toggle_bookmark,
    toggle_bookmark_api
)

urlpatterns = [
    # 1. 에피소드 상세 정보
    path('episode/detail/', EpisodeDetailAPIView.as_view(), name='episode-detail'),

    # 2. 에피소드 랜덤 조회 (v1 추가 및 경로 정렬)
    # 🚩 테스트하신 http://localhost:8000/api/stories/v1/episode/random/ 주소와 매칭됩니다.
    path("v1/episode/random/", StationStoryView.as_view(), name="random_episode_v1"),
    
    # 기존에 쓰던 경로들도 유지 (하위 호환성)
    path("episode/random/", StationStoryView.as_view(), name="random_episode"),
    path("episode/random/<str:station_identifier>/", StationStoryView.as_view(), name="random_episode_with_id"),
    
    # 3. 에피소드별 컷(Cuts) 목록
    path("v1/episodes/<int:episode_id>/cuts/", EpisodeCutListCreateView.as_view(), name="episode_cuts"),

    # 4. 역 식별자 기반 조회
    path('station/<str:station_identifier>/', StationStoryView.as_view(), name='station-story'),
    path('list/', WebtoonListView.as_view(), name='webtoon-list'),

    # 5. 북마크 관련
    path('bookmark/<int:episode_id>/', toggle_bookmark_api, name='toggle_bookmark_api'),
    
    # 6. HTML 렌더링용 (상세보기)
    path('episode/<int:episode_id>/', views.episode_detail, name='episode_detail'),
]