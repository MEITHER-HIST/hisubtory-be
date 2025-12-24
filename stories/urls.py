from django.urls import path
from . import views

urlpatterns = [
    # 브라우저 클릭 시 HTML 렌더링
    path('episode/<int:episode_id>/', views.episode_detail_view, name='episode_detail'),

    # 북마크 토글 (로그인 필요)
    path('episode/<int:episode_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
]
