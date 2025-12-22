from django.urls import path
from . import views

urlpatterns = [
    path('random-episode/', views.get_random_episode_api, name='get_random_episode'),
    path('test-map/', views.test_map_view, name='test_map'),
    path('select/<int:station_id>/', views.select_episode_api, name='select_episode_api'),
]
