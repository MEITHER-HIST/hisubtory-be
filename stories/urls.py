from django.urls import path
from . import views

urlpatterns = [
    # 브라우저 클릭 시 HTML 렌더링
    path('episode/<int:episode_id>/', views.episode_detail_view, name='episode_detail'),

    # API 호출용
    path('api/station/<int:station_id>/', views.station_stories_api, name='station_stories_api'),
]
