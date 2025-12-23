from django.shortcuts import render, get_object_or_404
from .models import Episode
from subway.models import Station
from library.models import UserViewedEpisode
import random

# ===== 브라우저용 뷰 =====
def episode_detail_view(request, episode_id):
    user = request.user if request.user.is_authenticated else None
    episode = get_object_or_404(Episode, id=episode_id)
    new_episode_button = False

    if user:
        station_id = episode.station.id
        viewed_episodes = UserViewedEpisode.objects.filter(user=user, episode__station_id=station_id)
        if viewed_episodes.exists():
            new_episode_button = True

        if request.GET.get('next') == 'true':
            unseen_episodes = Episode.objects.filter(station_id=station_id).exclude(
                id__in=viewed_episodes.values_list('episode_id', flat=True)
            )
            if unseen_episodes.exists():
                episode = random.choice(list(unseen_episodes))
                UserViewedEpisode.objects.get_or_create(user=user, episode=episode)
            new_episode_button = False

    context = {
        'episode': episode,
        'new_episode_button': new_episode_button,
    }
    return render(request, 'stories/episode_detail.html', context)


# ===== API용 뷰 =====
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EpisodeSerializer

@api_view(['GET'])
def station_stories_api(request, station_id):
    """
    JSON 형태로 반환하는 API 엔드포인트
    - 로그인 유저: 이미 본/안 본 에피 구분
    - 로그인 X: 랜덤 에피 반환
    """
    station = get_object_or_404(Station, id=station_id)
    user = request.user if request.user.is_authenticated else None

    episodes = Episode.objects.filter(station=station)
    if not episodes.exists():
        return Response({"message": "해당 역의 스토리가 없습니다."}, status=404)

    prev_episode = None
    new_episode_available = False
    not_viewed_episodes = list(episodes)

    if user:
        viewed_ids = set(UserViewedEpisode.objects.filter(user=user).values_list('episode_id', flat=True))
        already_viewed = [ep for ep in episodes if ep.id in viewed_ids]
        not_viewed_episodes = [ep for ep in episodes if ep.id not in viewed_ids]

        if already_viewed:
            prev_episode = already_viewed[-1]  # 직전에 본 에피
        if not_viewed_episodes:
            new_episode_available = True

    # 보여줄 에피 선택
    episode_to_show = random.choice(not_viewed_episodes) if not_viewed_episodes else random.choice(list(episodes))

    # DB 기록 남기기 (로그인 유저만)
    if user:
        UserViewedEpisode.objects.get_or_create(user=user, episode=episode_to_show)

    # JSON 응답
    data = {
        "episode": EpisodeSerializer(episode_to_show).data,
        "prev_episode": EpisodeSerializer(prev_episode).data if prev_episode else None,
        "new_episode_available": new_episode_available
    }
    return Response(data) 
