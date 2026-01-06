# pages/urls.py
from django.urls import path
from . import views_api

urlpatterns = [
    path("v1/main/", views_api.main_api_view, name="main_api"),
    path("v1/episode/pick/", views_api.pick_episode_api_view, name="pick_episode_api"),
    path("v1/episode/random/", views_api.random_episode_api_view, name="random_episode_api"),
]