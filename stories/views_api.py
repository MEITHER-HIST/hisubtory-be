import random
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Episode
from subway.models import Station
from library.models import UserViewedEpisode
from .serializers import EpisodeSerializer
from django.utils import timezone

# -----------------------------
# 에피소드 선택 API (역 버튼 / 랜덤 버튼)
# -----------------------------
@api_view(['GET'])
def pick_episode_view(request, station_id):
    mode = request.GET.get('mode', 'auto')
    user = request.user if request.user.is_authenticated else None

    station = get_object_or_404(Station, id=station_id)
    episodes = Episode.objects.filter(webtoon__station=station)

    if mode == 'unseen':
        if not user:
            return Response({"success": False, "message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        episodes = episodes.exclude(
            id__in=UserViewedEpisode.objects.filter(user=user).values_list('episode_id', flat=True)
        )

    if not episodes.exists():
        episodes = Episode.objects.filter(webtoon__station=station)

    if not episodes.exists():
        return Response({"success": False, "message": "No episodes available"}, status=status.HTTP_404_NOT_FOUND)

    episode = random.choice(list(episodes))

    if user:
        UserViewedEpisode.objects.get_or_create(user=user, episode=episode)

    serializer = EpisodeSerializer(episode)
    return Response({"success": True, "episode": serializer.data})


# -----------------------------
# 특정 에피 본 기록 저장 (선택적)
# -----------------------------
@api_view(['POST'])
def view_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    user = request.user
    if not user.is_authenticated:
        return Response({"success": False, "message": "Login required"}, status=status.HTTP_401_UNAUTHORIZED)

    UserViewedEpisode.objects.get_or_create(user=user, episode=episode)
    serializer = EpisodeSerializer(episode)
    return Response({"success": True, "episode": serializer.data})


# -----------------------------
# 에피소드 저장/토글
# -----------------------------
@api_view(['PUT'])
def toggle_save_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    user = request.user
    if not user.is_authenticated:
        return Response({"success": False, "message": "Login required"}, status=status.HTTP_401_UNAUTHORIZED)

    uve, created = UserViewedEpisode.objects.get_or_create(user=user, episode=episode)

    if uve.saved:
        uve.saved = False
        uve.saved_at = None
        action = "removed"
    else:
        uve.saved = True
        uve.saved_at = timezone.now()
        action = "added"

    uve.save()

    serializer = EpisodeSerializer(episode)
    return Response({"success": True, "action": action, "episode": serializer.data})
