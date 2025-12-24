from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Episode, Cut
from library.models import UserViewedEpisode, Bookmark
from subway.models import Station
import random

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

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from .models import Episode
# from .serializers import EpisodeSerializer
# from subway.models import Station
# import random

# @api_view(['GET'])
# def station_stories(request, station_id):
#     station = get_object_or_404(Station, id=station_id)
#     episodes = Episode.objects.filter(station=station)

#     if episodes.exists():
#         episode = random.choice(episodes)
#         serializer = EpisodeSerializer(episode)
#         return Response(serializer.data)
#     else:
#         return Response({"message": "해당 역의 스토리가 없습니다."}, status=404)

from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Cut
from .serializers import CutSerializer

class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")

    def perform_create(self, serializer):
        serializer.save(episode_id=self.kwargs["episode_id"])
