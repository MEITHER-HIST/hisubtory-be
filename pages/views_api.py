# pages/views_api.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db import connection
import random
import json
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.http import JsonResponse
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

    login(request, user)  # ✅ sessionid 발급됨
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
    # Episode에는 station_id가 없고, Episode -> Webtoon -> Station 구조
    qs = (
        Episode.objects
        .filter(webtoon__station_id=station_id, is_published=True)
        .select_related("webtoon", "webtoon__station")
    )
    if not qs.exists():
        return None
    # 데이터가 많아지면 order_by("?")는 비싸지만, 지금은 동작 우선
    return qs.order_by("?").first()


@require_GET
def main_api_view(request):
    # 노선 리스트(3호선만 active)
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

    # “스토리 존재하는 역” 빠르게 계산 (색상 표시용)
    story_station_ids = set(
        Episode.objects.filter(
            is_published=True,
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
            # ✅ 요구사항: 비로그인 = 역 클릭 불가
            "clickable": is_logged_in and has_story,
            "color": "green" if (has_story and is_logged_in) else "gray",
            "has_story": has_story,
        })

    return JsonResponse({
        "lines": line_list,
        "selected_line": line_obj.line_name,
        "stations": station_list,
        "show_random_button": bool(story_station_ids),  # 스토리 있는 역이 있으면 랜덤 가능
    })


@require_GET
def pick_episode_api_view(request):
    # ✅ 요구사항: 비로그인일 때 역 클릭 자체가 안돼야 하므로, 서버에서도 막아두기
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

    # Episode 모델엔 title이 없어서 subtitle/조합으로 내려줌
    title = ep.subtitle or f"{ep.webtoon.title} - EP{ep.episode_num}"

    return JsonResponse({
        "station_id": station_id,
        "station_name": ep.webtoon.station.station_name,
        "episode_id": ep.pk,              # ✅ ep.id 대신 ep.pk 안전
        "episode_num": ep.episode_num,
        "episode_title": title,
        "webtoon_id": ep.webtoon_id,
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

    # “해당 노선 + 스토리 있는 에피소드”에서 하나 랜덤
    qs = (
        Episode.objects
        .filter(is_published=True, webtoon__station_id__in=station_ids)
        .select_related("webtoon", "webtoon__station")
    )
    if not qs.exists():
        return JsonResponse({"message": "episode_not_found"}, status=404)

    ep = qs.order_by("?").first()
    title = ep.subtitle or f"{ep.webtoon.title} - EP{ep.episode_num}"

    return JsonResponse({
        "station_id": ep.webtoon.station_id,
        "station_name": ep.webtoon.station.station_name,
        "episode_id": ep.pk,
        "episode_num": ep.episode_num,
        "episode_title": title,
        "webtoon_id": ep.webtoon_id,
    })


# 마이페이지는 지금 모델이 없으니 "동작만" 시키려면 이렇게 스텁 처리
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
