# stories/urls.py 전문
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
    # 1. 에피소드 상세 정보 (App.tsx의 StoryScreen이 사용할 확률이 높음)
    # 최종 주소: /api/stories/episode/detail/
    path('episode/detail/', EpisodeDetailAPIView.as_view(), name='episode-detail'),

    # 2. 에피소드별 컷(Cuts) 목록
    # 최종 주소: /api/stories/v1/episodes/<int:episode_id>/cuts/
    path("v1/episodes/<int:episode_id>/cuts/", EpisodeCutListCreateView.as_view(), name="episode_cuts"),

    # 3. 역 식별자 기반 조회
    path('station/<str:station_identifier>/', StationStoryView.as_view(), name='station-story'),
    path('list/', WebtoonListView.as_view(), name='webtoon-list'),

    # 4. 북마크 관련
    path('bookmark/<int:episode_id>/', toggle_bookmark_api, name='toggle_bookmark_api'),
    
    # 5. HTML 렌더링용 (필요한 경우만 유지)
    path('episode/<int:episode_id>/', views.episode_detail, name='episode_detail'),
]