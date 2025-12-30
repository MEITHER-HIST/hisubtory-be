# pages/urls_api.py
from django.urls import path
from . import views_api

urlpatterns = [
    path("v1/main/", views_api.main_api_view, name="pages_main"),
    path("v1/episode/pick/", views_api.pick_episode_api_view, name="pages_episode_pick"),
    path("v1/episode/random/", views_api.random_episode_api_view, name="pages_episode_random"),
    path("v1/mypage/", views_api.mypage_api_view, name="pages_mypage"),
    path("v1/auth/mock-login/", views_api.mock_login_api_view),
    path("v1/auth/logout/", views_api.logout_api_view),
    path("v1/auth/me/", views_api.me_api_view),
]