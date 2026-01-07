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
    """현재 로그인 유무와 사용자명만 반환"""
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
    
    # 해당 노선의 역들 중 스토리가 있는 역 ID 추출
    story_station_ids = set(
        Episode.objects.filter(webtoon__station_id__in=stations.values_list("id", flat=True))
        .values_list("webtoon__station_id", flat=True).distinct()
    )

    is_auth = request.user.is_authenticated
    viewed_station_ids = set()
    if is_auth:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=request.user)
            .values_list("episode__webtoon__station_id", flat=True)
        )

    station_list = []
    for s in stations:
        is_viewed = (s.id in viewed_station_ids)
        has_story = (s.id in story_station_ids)
        
        # ✅ [수정] 프론트엔드 기획 변경 반영
        # 로그인 시: 스토리가 있으면 클릭 가능 (has_story)
        # 비로그인 시: 무조건 클릭 불가 (clickable = False) -> 오직 랜덤 버튼으로만 유도
        clickable = has_story if is_auth else False
        
        station_list.append({
            "id": s.id,
            "name": s.station_name,
            "clickable": clickable,
            # ✅ [수정] 비로그인 시에는 항상 gray로 표시되도록 is_viewed 무시
            "color": "green" if (is_auth and is_viewed) else "gray", 
            "is_viewed": is_viewed if is_auth else False,
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
    """
    특정 역 클릭 시 에피소드 ID 반환
    """
    station_id = request.GET.get("station_id")
    if not station_id:
        return JsonResponse({"success": False, "message": "station_id_required"}, status=400)

    ep = None
    # 1. 로그인 유저인 경우: 가장 최근에 본 에피소드 우선
    if request.user.is_authenticated:
        last_viewed = UserViewedEpisode.objects.filter(
            user=request.user, episode__webtoon__station_id=station_id
        ).select_related('episode').order_by('-viewed_at').first()
        if last_viewed:
            ep = last_viewed.episode

    # 2. 비로그인 유저이거나 본 기록이 없는 경우: 해당 역의 첫 에피소드
    if not ep:
        ep = Episode.objects.filter(webtoon__station_id=station_id).order_by('episode_num').first()
    
    if not ep:
        return JsonResponse({"success": False, "message": "no_episode"}, status=404)
    
    return JsonResponse({
        "success": True,
        "episode_id": str(ep.episode_id),
        "station_id": station_id,
        "title": getattr(ep, 'subtitle', f"EP {ep.episode_num}")
    })

@require_GET
def random_episode_api_view(request):
    """랜덤 에피소드 추천 (비로그인도 사용 가능)"""
    line_num = request.GET.get("line", "3")
    line_obj = Line.objects.filter(line_name=f"{line_num}호선").first()
    if not line_obj:
        return JsonResponse({"message": "line_not_found"}, status=404)

    station_ids = _station_ids_for_line(line_obj.id)
    # 스토리가 있는 역들 중에서만 랜덤 추출
    ep = Episode.objects.filter(webtoon__station_id__in=station_ids).order_by("?").first()
    
    if not ep: 
        return JsonResponse({"message": "no_episode"}, status=404)

    return JsonResponse({
        "success": True,
        "station_id": str(ep.webtoon.station_id),
        "station_name": ep.webtoon.station.station_name,
        "episode_id": str(ep.episode_id),
    })