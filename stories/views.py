<<<<<<< HEAD
from django.http import JsonResponse
from django.shortcuts import render
from .models import Episode
from .services import get_next_episode_with_ai_service
from library.models import UserActivity
from subway.models import Station

# stories/views.py
from .services import get_next_episode_with_ai_service, generate_four_images_service

def some_view(request, episode_id):
    episode = Episode.objects.get(id=episode_id)
    # 필요할 때 서비스를 호출하여 이미지를 생성합니다.
    if not episode.source_url:
        generate_four_images_service(episode)
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
    
# 역 선택 시 제공 이야기 확인
def select_episode_api(request, station_id):
    user = request.user
    episode = get_next_episode_with_ai_service(user, station_id)
    
    if not episode:
        return JsonResponse({'error': 'No episode found'}, status=404)

    # 연결된 4개의 이미지를 리스트로 만듭니다.
    image_list = []
    for img_obj in episode.images.all():
        image_list.append({
            'url': img_obj.image.url,
            'caption': img_obj.caption
        })

    data = {
        'id': episode.id,
        'title': episode.title,
        'subtitle': episode.subtitle,
        'history_summary': episode.history_summary,
        'images': image_list, # 4개의 이미지 세트 전달
    }
    return JsonResponse(data)
    
    
def test_map_view(request):
    """테스트를 위해 모든 역을 리스트로 보여주는 페이지"""
    stations = Station.objects.all()
    user = request.user if request.user.is_authenticated else None
    
    # 각 역마다 방문 여부를 미리 체크 (초록색 표시용)
    station_data = []
    for s in stations:
        is_visited = False
        if user:
            is_visited = UserActivity.objects.filter(user=user, episode__station=s).exists()
        station_data.append({'station': s, 'is_visited': is_visited})
        
    return render(request, 'stories/test_map.html', {'station_data': station_data})
=======
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Episode
from .serializers import EpisodeSerializer
from subway.models import Station
import random

@api_view(['GET'])
def station_stories(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    episodes = Episode.objects.filter(station=station)

    if episodes.exists():
        episode = random.choice(episodes)
        serializer = EpisodeSerializer(episode)
        return Response(serializer.data)
    else:
        return Response({"message": "해당 역의 스토리가 없습니다."}, status=404)
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
