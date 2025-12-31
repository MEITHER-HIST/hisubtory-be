from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.db import connection
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, login, logout
from subway.models import Line, Station
from stories.models import Episode

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
    return JsonResponse({
        "is_authenticated": bool(request.user and request.user.is_authenticated),
        "username": getattr(request.user, "username", None) if request.user.is_authenticated else None,
    })

def _station_ids_for_line(line_id: int) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT station_id FROM subway_station_lines WHERE line_id=%s",
            [line_id],
        )
        return [row[0] for row in cursor.fetchall()]

def _pick_random_episode_for_station(station_id: int):
    # ✅ 수정: station_id 대신 webtoon__station_id 사용
    qs = Episode.objects.filter(webtoon__station_id=station_id)
    if not qs.exists():
        return None
    return qs.order_by("?").first()

@require_GET
def main_api_view(request):
    lines = Line.objects.all()
    line_list = []
    for line in lines:
        is_active = (line.line_name == "3호선")
        display_name = line.line_name if is_active else f"{line.line_name} (준비중)"
        line_list.append({"id": line.id, "line_name": display_name, "is_active": is_active})

    line_num = request.GET.get("line", "3")
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3

    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()
    if not line_obj:
        return JsonResponse({"message": "line_not_found"}, status=404)

    station_ids = _station_ids_for_line(line_obj.id)
    stations = Station.objects.filter(id__in=station_ids, is_enabled=True)
    
    # ✅ 수정: station_id로 직접 필터링
    story_station_ids = set(
        Episode.objects.filter(
            webtoon__station_id__in=stations.values_list("id", flat=True),
        ).values_list("webtoon__station_id", flat=True).distinct()
    )

    is_logged_in = bool(request.user and request.user.is_authenticated)

    station_list = []
    for s in stations:
        has_story = (s.id in story_station_ids)
        station_list.append({
            "id": s.id,
            "name": s.station_name,
            "clickable": is_logged_in and has_story,
            "color": "green" if (has_story and is_logged_in) else "gray",
            "has_story": has_story,
        })

    return JsonResponse({
        "lines": line_list,
        "selected_line": line_obj.line_name,
        "stations": station_list,
        "show_random_button": bool(story_station_ids),
    })

@require_GET
def pick_episode_api_view(request):
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({"message": "login_required"}, status=401)

    station_id = request.GET.get("station_id")
    try:
        station_id = int(station_id)
    except (TypeError, ValueError):
        return JsonResponse({"message": "station_id_invalid"}, status=400)

    ep = _pick_random_episode_for_station(station_id)
    if not ep:
        return JsonResponse({"message": "episode_not_found"}, status=404)

    return JsonResponse({
        "station_id": station_id,
        "station_name": f"역 ID {station_id}",
        "episode_id": ep.pk,
        "episode_num": ep.episode_num,
        "episode_title": ep.title or ep.subtitle or f"EP{ep.episode_num}",
        "webtoon_id": ep.station_id,
    })
    
@require_GET
def random_episode_api_view(request):
    line_num = request.GET.get("line", "3")
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3

    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()
    if not line_obj:
        return JsonResponse({"message": "line_not_found"}, status=404)

    station_ids = _station_ids_for_line(line_obj.id)

    # ✅ 수정: webtoon__station_id 대신 station_id 사용 (에러 원인 제거)
    qs = Episode.objects.filter(station_id__in=station_ids)
    
    if not qs.exists():
        return JsonResponse({"message": "episode_not_found"}, status=404)

    ep = qs.order_by("?").first()
    return JsonResponse({
        "station_id": ep.station_id,
        "station_name": f"역 ID {ep.station_id}",
        "episode_id": ep.pk,
        "episode_num": ep.episode_num,
        "episode_title": ep.title or f"EP{ep.episode_num}",
        "webtoon_id": ep.station_id,
    })

@require_GET
def mypage_api_view(request):
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({"message": "login_required"}, status=401)

    user = request.user
    return JsonResponse({
        "user": {"id": user.id, "username": user.username},
        "recent_views": [],
        "bookmarked_episodes": [],
        "recent_count": 0,
        "bookmark_count": 0,
        "message": "mypage_not_implemented_yet",
    })