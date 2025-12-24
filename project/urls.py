from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.http import HttpResponse

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    path("health/", views.health),

    # admin
    path('admin/', admin.site.urls),

    # HTML
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    path('health/', health),
    path('stories/', include('stories.urls')),

]  
 