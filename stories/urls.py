from django.urls import path
from . import views

urlpatterns = [
    path('episode/<int:episode_id>/', views.episode_detail_view, name='episode_detail'),

    # 저장 토글 (로그인 필요)
    path('episode/<int:episode_id>/toggle_saved/', views.toggle_saved, name='toggle_saved'),
]
