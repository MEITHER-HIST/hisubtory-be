from django.urls import path
from . import views_api

urlpatterns = [
    # 메인 화면 및 에피소드 선택 관련
    path("v1/main/", views_api.main_api_view, name="pages_main"),
    path("v1/episode/pick/", views_api.pick_episode_api_view, name="pages_episode_pick"),
    path("v1/episode/random/", views_api.random_episode_api_view, name="pages_episode_random"),
    
    # 인증 관련 (MainScreen 및 App.tsx에서 사용)
    path("v1/auth/mock-login/", views_api.mock_login_api_view, name="pages_login"),
    path("v1/auth/logout/", views_api.logout_api_view, name="pages_logout"),
    path("v1/auth/me/", views_api.me_api_view, name="pages_me"),
]