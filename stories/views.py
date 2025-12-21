from django.http import JsonResponse
from .models import Episode  # 반드시 현재 앱의 모델을 참조해야 합니다.

# stories/views.py
from .services import generate_episode_image_service

def some_view(request, episode_id):
    episode = Episode.objects.get(id=episode_id)
    # 필요할 때 서비스를 호출하여 이미지를 생성합니다.
    if not episode.source_url:
        generate_episode_image_service(episode)
    # ... 나머지 로직


def get_random_episode_api(request):
    # 모든 에피소드 중 하나라도 있는지 확인
    episode = Episode.objects.all().order_by('last_viewed_at').first()

    if not episode:
        # 데이터가 없을 때 전체 개수를 출력하여 디버깅
        total_count = Episode.objects.count()
        return JsonResponse({
            "status": "error", 
            "message": f"DB에 에피소드가 0개입니다. (현재 감지된 개수: {total_count}개)",
            "tip": "python manage.py shell에서 데이터를 다시 생성해 보세요."
        }, status=404)

    # 데이터가 있다면 기존 로직 실행 (services.py 호출)
    from .services import get_or_generate_episode_logic
    episode = get_or_generate_episode_logic()

    return JsonResponse({
        "status": "success",
        "data": {
            "station": episode.station.name,
            "subtitle": episode.subtitle,
            "image_url": episode.source_url.url if episode.source_url else None
        }
    })