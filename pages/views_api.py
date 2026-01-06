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

@require_GET
def main_api_view(request):
    line_num = request.GET.get("line", "3")
    line_obj = Line.objects.filter(line_name=f"{line_num}호선").first()
    if not line_obj:
        return JsonResponse({"success": False, "message": "line_not_found"}, status=404)

    station_ids = _station_ids_for_line(line_obj.id)
    stations = Station.objects.filter(id__in=station_ids, is_enabled=True)
    
    story_station_ids = set(
        Episode.objects.filter(
            webtoon__station_id__in=stations.values_list("id", flat=True)
        ).values_list("webtoon__station_id", flat=True).distinct()
    )

    is_logged_in = bool(request.user and request.user.is_authenticated)
    
    viewed_station_ids = set()
    if is_logged_in:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=request.user)
            .values_list("episode__webtoon__station_id", flat=True)
        )

    station_list = []
    for s in stations:
        is_viewed = (s.id in viewed_station_ids)
        has_story = (s.id in story_station_ids)
        
        # [조건 반영] 봤던 역(is_viewed)만 초록색 및 클릭 가능
        station_list.append({
            "id": s.id,
            "name": s.station_name,
            "clickable": is_viewed,
            "color": "green" if is_viewed else "gray", 
            "is_viewed": is_viewed,
            "has_story": has_story,
        })

    return JsonResponse({
        "success": True,
        "stations": station_list,
        "selected_line": line_obj.line_name,
        "show_random_button": bool(story_station_ids),
    })

@require_GET
def pick_episode_api_view(request):
    """역 클릭 시 해당 역의 에피소드 정보를 반환하는 핵심 뷰"""
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({"success": False, "message": "login_required"}, status=401)

    station_id = request.GET.get("station_id")
    if not station_id:
        return JsonResponse({"success": False, "message": "station_id_required"}, status=400)

    # 1. 시청 기록(UserViewedEpisode)에서 해당 역의 가장 최근 에피소드 탐색
    last_viewed = UserViewedEpisode.objects.filter(
        user=request.user, 
        episode__webtoon__station_id=station_id
    ).select_related('episode').order_by('-viewed_at').first()

    if last_viewed:
        ep = last_viewed.episode
    else:
        # 2. 기록이 없으면(초록색인데 기록이 없는 예외 상황 대비) 해당 역의 첫 에피소드 탐색
        ep = Episode.objects.filter(webtoon__station_id=station_id).first()

    if not ep:
        return JsonResponse({"success": False, "message": "해당 역에 연결된 에피소드가 없습니다."}, status=404)

    return JsonResponse({
        "success": True,
        "station_id": str(station_id),
        "episode_id": str(ep.episode_id), # 프론트엔드와 일관성을 위해 문자열로 변환
        "webtoon_id": str(ep.webtoon_id),
        "title": getattr(ep, 'subtitle', f"EP {ep.episode_num}")
    })

@require_GET
def random_episode_api_view(request):
    line_num = request.GET.get("line", "3")
    line_obj = Line.objects.filter(line_name=f"{line_num}호선").first()
    if not line_obj:
        return JsonResponse({"message": "line_not_found"}, status=404)

    station_ids = _station_ids_for_line(line_obj.id)
    qs = Episode.objects.filter(webtoon__station_id__in=station_ids).select_related('webtoon__station')
    
    if not qs.exists():
        return JsonResponse({"message": "episode_not_found"}, status=404)

    ep = qs.order_by("?").first()
    return JsonResponse({
        "station_id": str(ep.webtoon.station_id),
        "station_name": ep.webtoon.station.station_name,
        "episode_id": str(ep.episode_id),
        "webtoon_id": str(ep.webtoon_id),
    })

@require_GET
def mypage_api_view(request):
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({"message": "login_required"}, status=401)
    return JsonResponse({"message": "mypage_not_implemented_yet"})