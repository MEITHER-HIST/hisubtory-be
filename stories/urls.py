from django.contrib import admin
from django.urls import path, include
from stories.views import EpisodeCutListCreateView
from . import views

urlpatterns = [
    # 브라우저 클릭 시 HTML 렌더링
    path('episode/<int:episode_id>/', views.episode_detail_view, name='episode_detail'),
    # pages, stories API
    path('api/v1/lines/', include('pages.urls_api')),
    path('api/v1/stories/', include('stories.urls_api')),
    path("api/v1/episodes/<int:episode_id>/cuts/", EpisodeCutListCreateView.as_view(), name="episode_cuts"),
]
