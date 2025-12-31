import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
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

# 1. HTML 상세 뷰 (웹용)
def episode_detail(request, episode_id):
    # ✅ PK 필드명 반영: episode_id
    episode = get_object_or_404(Episode, episode_id=episode_id)

    # ✅ 정렬 필드 반영: cut_order
    cuts = episode.cuts.all().order_by('cut_order')

    if request.user.is_authenticated:
        UserViewedEpisode.objects.get_or_create(
            user=request.user, 
            episode=episode
        )

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user, 
            episode=episode
        ).exists()

    context = {
        'episode': episode,
        'cuts': cuts,
        'is_bookmarked': is_bookmarked,
        # ✅ 계층 구조 반영: Episode -> Webtoon -> Station
        'station_name': episode.webtoon.station.station_name, 
    }
    return render(request, 'stories/episode_detail.html', context)

# 2. 리액트 연동 API 뷰
class EpisodeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        episode_id = self.request.query_params.get('episode_id')
        if not episode_id:
            return Response({"success": False, "message": "id missing"}, status=400)
        
        # ✅ 수정: id -> episode_id
        episode = get_object_or_404(Episode, episode_id=episode_id)
        serializer = self.get_serializer(episode)
        return Response({
            "success": True, 
            "episode": serializer.data, 
            "cuts": serializer.data.get('cuts', [])
        })

# 3. StationStoryView
class StationStoryView(APIView):
    def get(self, request, station_identifier):
        decoded_name = unquote(station_identifier)
        try:
            # ✅ 수정: station_id 직접 참조 대신 webtoon__station_id 사용
            if decoded_name.isdigit():
                episode = Episode.objects.filter(webtoon__station_id=decoded_name).first()
            else:
                episode = Episode.objects.first()
                
            if not episode:
                return Response({"message": "No data"}, status=404)
            serializer = StorySerializer(episode)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# 4. 에피소드별 컷 관리 API
class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # ✅ 수정: episode_id 필터링
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")
    
    def perform_create(self, serializer):
        # ✅ 수정: episode_id로 저장
        serializer.save(episode_id=self.kwargs["episode_id"])

# 5. 북마크 토글
@login_required
def toggle_bookmark(request, episode_id):
    # ✅ 수정: id -> episode_id
    episode = get_object_or_404(Episode, episode_id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()
    return redirect('episode_detail', episode_id=episode_id)