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
# 에피소드 선택 API (역 버튼 / 랜덤 버튼)
# -----------------------------
@api_view(['GET'])
def pick_episode_view(request, station_id):
    """
    station_id 기준 에피소드 선택
    ?mode=auto/unseen
    - mode=unseen → 역 버튼 클릭, 로그인 유저만 가능
    - mode=auto   → 랜덤 버튼 클릭, 로그인/비로그인 모두 가능
    """
    mode = request.GET.get('mode', 'auto')
    user = request.user if request.user.is_authenticated else None

    station = get_object_or_404(Station, id=station_id)
    episodes = Episode.objects.filter(station=station)

    # -----------------------------
    # 역 버튼 클릭: 미시청 우선
    # -----------------------------
    if mode == 'unseen':
        if not user:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # 로그인 유저만 미시청 에피 선택
        episodes = episodes.exclude(
            id__in=UserViewedEpisode.objects.filter(user=user)
            .values_list('episode_id', flat=True)
        )

    # -----------------------------
    # 선택 가능한 에피가 없으면 전체 에피로 fallback
    # -----------------------------
    if not episodes.exists():
        episodes = Episode.objects.filter(station=station)

    if not episodes.exists():
        return Response(
            {"success": False, "message": "No episodes available"},
            status=status.HTTP_404_NOT_FOUND
        )

    # -----------------------------
    # 랜덤 선택
    # -----------------------------
    episode = random.choice(list(episodes))

    # -----------------------------
    # 로그인 유저 본 기록 저장
    # -----------------------------
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
# 에피소드 즐겨찾기/토글
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
