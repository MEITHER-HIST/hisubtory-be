from django.urls import path
from . import views_api

urlpatterns = [
    # 특정 역의 랜덤/미시청 에피소드 선택
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
