# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # <int: >를 <str: >로 바꿔야 한글(역 이름)이 들어와도 통과됩니다.
    path('api/stories/station/<str:station_identifier>/', views.StationStoryView.as_view()),
]