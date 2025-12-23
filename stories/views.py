from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Episode, Cut
from library.models import UserViewedEpisode, Bookmark
from subway.models import Station
import random

# ===== 브라우저용 뷰 =====
def episode_detail_view(request, episode_id):
    user = request.user if request.user.is_authenticated else None
    episode = get_object_or_404(Episode, id=episode_id)

    # 컷 4개 가져오기
    cuts = episode.cuts.all()[:4]

    # 다른 에피소드 확인 (같은 역)
    all_episodes = Episode.objects.filter(station=episode.station)
    other_episodes = all_episodes.exclude(id=episode.id)

    # 북마크 상태
    is_bookmarked = False
    if user:
        is_bookmarked = Bookmark.objects.filter(user=user, episode=episode).exists()

    # 새 에피소드 버튼 처리 (이미 본 적 있는지)
    new_episode_button = False
    if user:
        viewed_episodes = UserViewedEpisode.objects.filter(user=user, episode__station_id=episode.station.id)
        if viewed_episodes.exists():
            new_episode_button = True

        # GET param으로 다음 에피 선택
        if request.GET.get('next') == 'true':
            unseen_episodes = Episode.objects.filter(station=episode.station).exclude(
                id__in=viewed_episodes.values_list('episode_id', flat=True)
            )
            if unseen_episodes.exists():
                episode = random.choice(list(unseen_episodes))
                UserViewedEpisode.objects.get_or_create(user=user, episode=episode)
                cuts = episode.cuts.all()[:4]  # 컷 갱신
            new_episode_button = False

    context = {
        'episode': episode,
        'cuts': cuts,
        'other_episodes': other_episodes,
        'new_episode_button': new_episode_button,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'stories/episode_detail.html', context)


# ===== 북마크 토글 뷰 =====
@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()  # 이미 북마크 되어있으면 취소
    return redirect('episode_detail', episode_id=episode_id)


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

    data = {
        "episode": EpisodeSerializer(episode_to_show).data,
        "prev_episode": EpisodeSerializer(prev_episode).data if prev_episode else None,
        "new_episode_available": new_episode_available
    }
    return Response(data) 
