from django.http import JsonResponse
from .services import get_or_generate_episode_logic

def get_episode_api(request):
    episode = get_or_generate_episode_logic()

    if episode:
        return JsonResponse({
            "status": "success",
            "station_name": episode.station.station_name,
            "episode_num": episode.episode_num,
            "subtitle": episode.subtitle,
            "history_summary": episode.history_summary,
            "image_url": episode.source_url.url # 생성된 이미지 경로
        })
    return JsonResponse({"status": "error", "message": "No data"}, status=404)