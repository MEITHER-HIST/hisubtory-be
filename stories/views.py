import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404  # <--- 이것도 get_object에서 쓰이니 확인!

from rest_framework import generics
from rest_framework.response import Response  # <--- 이 줄이 핵심입니다!
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from .models import Webtoon, Episode, Cut
from .serializers import EpisodeSerializer, CutSerializer
from library.models import UserViewedEpisode, Bookmark
from subway.models import Station

# ===== [HTML] 에피소드 상세 뷰 (기존 템플릿 렌더링용) =====
def episode_detail_view(request, episode_id):
    user = request.user if request.user.is_authenticated else None
    # DB 컬럼명에 맞춰 id 대신 episode_id 사용
    episode = get_object_or_404(Episode, episode_id=episode_id)

    # 역방향 참조 (related_name이 cuts라고 가정)
    cuts = episode.cuts.all().order_by('cut_order')[:4]

    # 같은 웹툰(역)에 속한 다른 에피소드들
    other_episodes = Episode.objects.filter(webtoon=episode.webtoon).exclude(episode_id=episode.episode_id)

    is_bookmarked = False
    if user:
        is_bookmarked = Bookmark.objects.filter(user=user, episode=episode).exists()

    context = {
        'episode': episode,
        'cuts': cuts,
        'other_episodes': other_episodes,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'stories/episode_detail.html', context)


# ===== [API] 에피소드 상세 뷰 (프론트엔드 리액트/모바일용) =====
class EpisodeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        episode_id = self.request.query_params.get('episode_id')
        if not episode_id:
            return Response({"success": False, "message": "episode_id가 없습니다."}, status=400)

        # DB에서 에피소드 찾기
        episode = get_object_or_404(Episode, episode_id=episode_id)
        serializer = self.get_serializer(episode)
        
        # 프론트엔드가 기대하는 { success, episode, cuts } 구조로 반환
        return Response({
            "success": True,
            "episode": {
                "id": serializer.data['episode_id'],
                "episode_num": serializer.data['episode_num'],
                "episode_title": serializer.data['subtitle'] or f"{serializer.data['episode_num']}화",
                "station_name": "대화", # 임시값, 필요시 serializer에서 webtoon.station 정보 참조
                "webtoon_id": serializer.data['webtoon'],
            },
            "cuts": serializer.data['cuts'] # Serializer가 이미 가져온 cuts 리스트
        })


# ===== [API] 에피소드별 컷 리스트/생성 뷰 =====
class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # URL 경로의 <int:episode_id>를 통해 필터링
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")

    def perform_create(self, serializer):
        serializer.save(episode_id=self.kwargs["episode_id"])


# ===== [기능] 북마크 토글 =====
@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()
    return redirect('episode_detail', episode_id=episode_id)