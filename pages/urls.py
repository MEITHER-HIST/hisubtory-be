from django.urls import path, include
from . import views, api_views

urlpatterns = [
    # 템플릿 뷰
    path('', views.main_view, name='main'),
    path('mypage/', views.mypage_view, name='mypage'),

    # API 뷰
    path('api/v1/lines', api_views.lines_list, name='lines_list'),
    path('api/v1/lines/<str:line_id>', api_views.line_detail, name='line_detail'),
    path('api/v1/stations/<int:station_id>/random_episode', api_views.random_episode_view, name='random_episode'),
    path("accounts/", include("accounts.urls")),
    path("api/accounts/", include("accounts.urls_api")),
]
