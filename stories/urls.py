from django.urls import path
from . import views

urlpatterns = [
    path('random-episode/', views.get_random_episode_api, name='get_random_episode'),
]