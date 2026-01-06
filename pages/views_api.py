from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.db import connection
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, login, logout
from subway.models import Line, Station
from stories.models import Episode, Webtoon
from library.models import UserViewedEpisode

User = get_user_model()

@csrf_exempt
@require_POST
def mock_login_api_view(request):
    data = json.loads(request.body or "{}")
    username = (data.get("username") or "").strip()
    if not username:
        return JsonResponse({"message": "username_required"}, status=400)
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_unusable_password()
        user.save()
    login(request, user)
    return JsonResponse({"username": user.username})

@csrf_exempt
@require_POST
def logout_api_view(request):
    logout(request)
    return JsonResponse({"ok": True})

@require_GET
def me_api_view(request):
    """현재 로그인 유무와 사용자명만 반환 (마이페이지 기본 진입용)"""
    return JsonResponse({
        "success": True,
        "is_authenticated": bool(request.user and request.user.is_authenticated),
        "username": getattr(request.user, "username", None) if request.user.is_authenticated else None,
    })

def _station_ids_for_line(line_id: int) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT station_id FROM subway_station_lines WHERE line_id=%s", [line_id])
        return [row[0] for row in cursor.fetchall()]

@require_GET
def main_api_view(request):
    line_num = request.GET.get("line", "3")
    line_obj = Line.objects.filter(line_name=f"{line_num}호선").first()
    if not line_obj:
        return JsonResponse({"success": False, "message": "line_not_found"}, status=404)

    station_ids = _station_ids_for_line(line_obj.id)
    stations = Station.objects.filter(id__in=station_ids, is_enabled=True)
    
    story_station_ids = set(
        Episode.objects.filter(webtoon__station_id__in=stations.values_list("id", flat=True))
        .values_list("webtoon__station_id", flat=True).distinct()
    )

    viewed_station_ids = set()
    if request.user.is_authenticated:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=request.user)
            .values_list("episode__webtoon__station_id", flat=True)
        )

    station_list = []
    for s in stations:
        is_viewed = (s.id in viewed_station_ids)
        station_list.append({
            "id": s.id,
            "name": s.station_name,
            "clickable": is_viewed,
            "color": "green" if is_viewed else "gray", 
            "is_viewed": is_viewed,
            "has_story": (s.id in story_station_ids),
        })

    return JsonResponse({
        "success": True,
        "stations": station_list,
        "selected_line": line_obj.line_name,
        "show_random_button": bool(story_station_ids),
    })

@require_GET
def pick_episode_api_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "login_required"}, status=401)
    station_id = request.GET.get("station_id")
    last_viewed = UserViewedEpisode.objects.filter(
        user=request.user, episode__webtoon__station_id=station_id
    ).select_related('episode').order_by('-viewed_at').first()
    ep = last_viewed.episode if last_viewed else Episode.objects.filter(webtoon__station_id=station_id).first()
    if not ep:
        return JsonResponse({"success": False, "message": "no_episode"}, status=404)
    return JsonResponse({
        "success": True,
        "episode_id": str(ep.episode_id),
        "title": getattr(ep, 'subtitle', f"EP {ep.episode_num}")
    })

@require_GET
def random_episode_api_view(request):
    line_num = request.GET.get("line", "3")
    line_obj = Line.objects.filter(line_name=f"{line_num}호선").first()
    station_ids = _station_ids_for_line(line_obj.id)
    ep = Episode.objects.filter(webtoon__station_id__in=station_ids).order_by("?").first()
    if not ep: return JsonResponse({"message": "no_episode"}, status=404)
    return JsonResponse({
        "station_id": str(ep.webtoon.station_id),
        "station_name": ep.webtoon.station.station_name,
        "episode_id": str(ep.episode_id),
    })