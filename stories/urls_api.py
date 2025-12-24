from django.urls import path
from . import views_api

urlpatterns = [
    # 특정 역의 랜덤/미시청 에피소드 선택
    path(
        'stations/<int:station_id>/episodes/pick/',
        views_api.pick_episode_view,
        name='pick_episode'
    ),

    # 특정 에피 본 기록 저장
    path(
        'episodes/<int:episode_id>/view/',
        views_api.view_episode,
        name='view_episode'
    ),

    # 에피소드 저장/토글
    path(
        'episodes/<int:episode_id>/toggle_saved/',
        views_api.toggle_save_episode,
        name='toggle_saved'
    ),
]
