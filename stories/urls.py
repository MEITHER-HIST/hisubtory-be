<<<<<<< HEAD
from django.urls import path
from . import views

urlpatterns = [
    path('random-episode/', views.get_random_episode_api, name='get_random_episode'),
    path('test-map/', views.test_map_view, name='test_map'),
    path('select/<int:station_id>/', views.select_episode_api, name='select_episode_api'),
]
=======
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # account 앱 URL 포함
    path('account/', include('account.urls')),

    # pages, stories API
    path('api/v1/lines/', include('pages.urls_api')),
    path('api/v1/stories/', include('stories.urls_api')),
]
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
