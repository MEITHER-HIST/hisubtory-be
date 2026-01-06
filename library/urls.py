from django.urls import path
from library import views as library_views

urlpatterns = [
    # ✅ 프론트엔드 fetch("/api/library/history/")와 매칭됩니다.
    path("history/", library_views.get_user_history_api, name="library_history"),
]