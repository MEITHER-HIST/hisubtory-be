from django.http import JsonResponse
from .services import get_or_generate_episode_logic

def get_random_episode_api(request):
    episode = get_or_generate_episode_logic()

    if episode:
        return JsonResponse({
            "status": "success",
            "data": {
                "station_name": episode.station.station_name,
                "episode_num": episode.episode_num,
                "subtitle": episode.subtitle,
                "history_summary": episode.history_summary,
                "image_url": episode.source_url.url if episode.source_url else None
            }
        })
    
    return JsonResponse({"status": "error", "message": "에피소드를 찾을 수 없습니다."}, status=404)