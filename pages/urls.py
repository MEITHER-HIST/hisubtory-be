from django.urls import path
from . import views_api as views

app_name = "pages"

urlpatterns = [
    path('v1/main/', views.main_view, name='main_api'),
    path("v1/episode/pick/", views.pick_episode_api_view, name="pick_episode_api"),
    path('v1/episode/random/', views.get_random_episode_api, name='random_episode_api'),
]