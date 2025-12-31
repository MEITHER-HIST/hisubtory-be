# library/views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserViewedEpisode, Bookmark
from accounts.views import UnsafeSessionAuthentication # 아까 만든 클래스 재사용 혹은 새로 정의
from rest_framework.authentication import SessionAuthentication

class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request): return

@api_view(['GET'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_history_api(request):
    user = request.user
    # select_related를 명세 계층에 맞게 수정
    viewed_qs = UserViewedEpisode.objects.filter(user=user).select_related(
        'episode__webtoon__station'
    ).order_by('-viewed_at')[:10]
    
    bookmark_qs = Bookmark.objects.filter(user=user).select_related(
        'episode__webtoon__station'
    ).order_by('-created_at')

    recent_data = [{
        "id": str(v.episode.episode_id),
        "title": v.episode.webtoon.title,
        "stationName": v.episode.webtoon.station.station_name, # station_name으로 수정
        "imageUrl": v.episode.webtoon.thumbnail.url if v.episode.webtoon.thumbnail else "",
        "content": v.episode.subtitle
    } for v in viewed_qs]

    saved_data = [{
        "id": str(b.episode.episode_id),
        "title": b.episode.webtoon.title,
        "content": b.episode.subtitle
    } for b in bookmark_qs]

    return Response({"recent": recent_data, "saved": saved_data})