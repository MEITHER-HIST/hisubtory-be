import random
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Episode
from subway.models import Station
from library.models import UserViewedEpisode, Bookmark
from .serializers import EpisodeSerializer

# -----------------------------
# 역 클릭 시 랜덤/미시청 에피 선택
# -----------------------------
@api_view(['GET'])
def pick_episode_view(request, station_id):
    """
    station_id 기준 랜덤 에피소드 선택
    ?mode=auto/unseen
    로그인 유무 상관없이 가능
    """
    mode = request.GET.get('mode', 'auto')
    user = request.user if request.user.is_authenticated else None

    station = get_object_or_404(Station, id=station_id)
    episodes = Episode.objects.filter(station=station)

    if user and mode == 'unseen':
        episodes = episodes.exclude(
            id__in=UserViewedEpisode.objects.filter(user=user)
            .values_list('episode_id', flat=True)
        )

    if not episodes.exists():
        # unseen 모드여도 선택 가능 에피 없다면 전체 에피로 fallback
        episodes = Episode.objects.filter(station=station)

    if not episodes.exists():
        return Response({"success": False, "message": "No episodes available"}, status=status.HTTP_404_NOT_FOUND)

    episode = random.choice(list(episodes))

    # 로그인 유저면 본 기록 저장
    if user:
        UserViewedEpisode.objects.get_or_create(user=user, episode=episode)

    serializer = EpisodeSerializer(episode)
    return Response({"success": True, "episode": serializer.data})


# -----------------------------
# 에피소드 본 기록 저장
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
# 에피소드 즐겨찾기/저장 (토글)
# -----------------------------
@api_view(['PUT'])
def save_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    user = request.user
    if not user.is_authenticated:
        return Response({"success": False, "message": "Login required"}, status=status.HTTP_401_UNAUTHORIZED)

    bookmark, created = Bookmark.objects.get_or_create(user=user, episode=episode)
    if not created:
        # 이미 즐겨찾기 되어 있으면 제거
        bookmark.delete()
        action = "removed"
    else:
        action = "added"

    serializer = EpisodeSerializer(episode)
    return Response({"success": True, "action": action, "episode": serializer.data})
