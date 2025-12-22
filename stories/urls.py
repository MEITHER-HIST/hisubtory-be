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