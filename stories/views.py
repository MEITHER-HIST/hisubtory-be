import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from urllib.parse import unquote

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from .models import Webtoon, Episode, Cut
from .serializers import EpisodeSerializer, CutSerializer, StorySerializer
from library.models import UserViewedEpisode, Bookmark
from subway.models import Station

# 1. [HTML] 에피소드 상세 페이지 뷰 (기존 웹 템플릿용)
def episode_detail_view(request, episode_id):
    user = request.user if request.user.is_authenticated else None
    episode = get_object_or_404(Episode, episode_id=episode_id)
    
    if user:
        UserViewedEpisode.objects.update_or_create(
            user=user, 
            episode=episode,
            defaults={'viewed_at': timezone.now()} 
        )

    # 컷 정렬 기준 유지
    cuts = episode.cuts.all().order_by('cut_order')[:4]

    # 같은 웹툰(역)의 다른 에피소드들
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


# 2. [API] 에피소드 상세 뷰 (리액트 StoryScreen.tsx 연동용)
class EpisodeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        episode_id = self.request.query_params.get('episode_id')
        if not episode_id:
            return Response({"success": False, "message": "episode_id가 없습니다."}, status=400)

        episode = get_object_or_404(Episode, episode_id=episode_id)
        serializer = self.get_serializer(episode)
        
        # 프론트엔드 StoryScreen.tsx의 data.episode / data.cuts 구조에 맞춤
        return Response({
            "success": True,
            "episode": {
                "id": serializer.data.get('episode_id'),
                "episode_num": serializer.data.get('episode_num'),
                "episode_title": serializer.data.get('subtitle') or f"{serializer.data.get('episode_num')}화",
                "station_name": episode.webtoon.station.station_name if episode.webtoon and episode.webtoon.station else "알 수 없음",
                "webtoon_id": serializer.data.get('webtoon'),
            },
            "cuts": serializer.data.get('cuts', [])
        })


# 3. [API] 역 식별자 기반 스토리 조회 (팀원 추가 기능 보존)
class StationStoryView(APIView):
    def get(self, request, station_identifier):
        decoded_name = unquote(station_identifier)
        try:
            if decoded_name.isdigit():
                episode = Episode.objects.filter(webtoon__station_id=decoded_name).first()
            else:
                episode = Episode.objects.filter(webtoon__station__station_name__contains=decoded_name).first()

            if not episode:
                return Response({"message": "데이터가 없습니다."}, status=404)

            serializer = StorySerializer(episode)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# 4. [API] 에피소드별 컷 리스트 조회 및 생성
class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")

    def perform_create(self, serializer):
        serializer.save(episode_id=self.kwargs["episode_id"])


# 5. [기능] 북마크 토글
@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()
    return redirect('episode_detail', episode_id=episode_id)


# 6. [API] 기존 호환용 역별 스토리 목록 (팀원 코드 유지)
@api_view(['GET'])
def station_stories_api(request, station_id):
    episodes = Episode.objects.filter(webtoon__station_id=station_id)
    if not episodes.exists():
        return Response({"message": "해당 역의 스토리가 없습니다."}, status=404)

    serializer = StorySerializer(episodes.first())
    return Response(serializer.data)