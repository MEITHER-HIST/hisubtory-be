from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Station
from stories.models import Episode 
import random

# --- 1. 노선 활성 역 목록 API ---
def station_list_api(request):
    line = request.GET.get('line', '3호선')
    stations = Station.objects.filter(line=line, is_enabled=True)
    data = []
    for s in stations:
        data.append({
            "id": s.id,
            "name": s.name,
            "image": s.image.url if s.image else None,  # 역 이미지가 있다면
        })
    return JsonResponse(data, safe=False)

# --- 2. 랜덤 역 선택 API ---
def random_station_api(request):
    line = request.GET.get('line', '3호선')
    stations = Station.objects.filter(line=line, is_enabled=True)
    station = random.choice(list(stations)) if stations else None
    if not station:
        return JsonResponse({"message": "no_station"}, status=404)
    data = {
        "id": station.id,
        "name": station.name,
        "image": station.image.url if station.image else None,
    }
    return JsonResponse(data)

# --- 3. 랜덤 에피소드 API ---
def random_episode_api(request, station_id):
    station = get_object_or_404(Station, id=station_id, is_enabled=True)
    episodes = Episode.objects.filter(station=station)
    episode = random.choice(list(episodes)) if episodes else None
    if not episode:
        return JsonResponse({"message": "no_episode"}, status=404)
    data = {
        "id": episode.id,
        "title": episode.title,
        "image": episode.image.url if episode.image else None,
        "station": {"id": station.id, "name": station.name},
    }
    return JsonResponse(data)