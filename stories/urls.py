from django.urls import path
from . import views

urlpatterns = [
    # 에피소드 상세 페이지
    path('<int:episode_id>/', views.episode_detail_view, name='episode_detail'),
]