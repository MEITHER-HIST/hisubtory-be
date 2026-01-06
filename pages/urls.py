from django.urls import path
from . import views

urlpatterns = [
    # Main 화면 데이터 (역 목록 등)
    path('v1/main/', views.main_view, name='main_api'),
    
    # ✅ 리액트가 호출하는 바로 그 경로!
    path('v1/episode/random/', views.get_random_episode_api, name='random_episode_api'),
]