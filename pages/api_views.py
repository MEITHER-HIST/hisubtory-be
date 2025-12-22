from django.http import JsonResponse
from subway.models import Station
from stories.models import Episode
import random

# 1. 노선 목록 조회
def lines_list(request):
    lines = Station.objects.filter(is_enabled=True).values_list('line', flat=True).distinct()
    return JsonResponse({"status": "lines_list_ok", "lines": list(lines)})

# 2. 선택 노선 + 역 목록 조회
def line_detail(request, line_id):
    stations = Station.objects.filter(line=line_id, is_enabled=True)
    if not stations.exists():
        return JsonResponse({"status": "line_not_found"}, status=404)

    station_list = [{"id": s.id, "name": s.name} for s in stations]
    return JsonResponse({
        "status": "line_detail_ok",
        "line": line_id,
        "stations": station_list
    })

# 3. 랜덤 역 + 에피소드 조회
def random_episode_view(request, station_id):
    try:
        station = Station.objects.get(id=station_id, is_enabled=True)
    except Station.DoesNotExist:
        return JsonResponse({"status": "station_not_found"}, status=404)

    episodes = Episode.objects.filter(station=station)
    if not episodes.exists():
        return JsonResponse({"status": "episode_not_found"}, status=404)

    episode = random.choice(list(episodes))
    return JsonResponse({
        "status": "episode_ok",
        "station": {"id": station.id, "name": station.name},
        "episode": {
            "id": episode.id,
            "title": episode.title,
            "image_url": episode.image.url if episode.image else None
        }
    })