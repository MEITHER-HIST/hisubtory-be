from django.urls import path
from . import views_api
from .views import StationStoryView # 클래스형 뷰를 가져옵니다.

urlpatterns = [
    # 🚩 새로 추가: 프론트엔드 요청용 랜덤 에피소드 API
    # 최종 주소: /api/stories/v1/episode/random/
    path(
        'v1/episode/random/', 
        StationStoryView.as_view(), 
        name='random_episode_v1'
    ),

    # 기존 역별 에피소드 선택 (이미 있던 것)
    path(
        'stations/<int:station_id>/episodes/pick',
        views_api.pick_episode_view,
        name='pick_episode'
    ),

    # 에피소드 본 기록 저장
    path(
        'episodes/<int:episode_id>/view',
        views_api.view_episode,
        name='view_episode'
    ),

    # 에피소드 즐겨찾기/저장 (토글)
    path(
        'episodes/<int:episode_id>/save',
        views_api.save_episode,
        name='save_episode'
    ),
]