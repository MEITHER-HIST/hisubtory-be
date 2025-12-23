from django.urls import path
from . import api_views

urlpatterns = [
    # 노선 관련 API
    path('v1/lines', api_views.lines_list, name='lines_list'),
    path('v1/lines/<str:line_id>', api_views.line_detail, name='line_detail'),

    # 랜덤 에피소드 API
    path('v1/stations/<int:station_id>/random_episode', api_views.random_episode_view, name='random_episode'),
]
 