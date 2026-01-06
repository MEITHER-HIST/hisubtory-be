import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from urllib.parse import unquote
from django.db import IntegrityError, transaction

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .models import Webtoon, Episode, Cut
from .serializers import EpisodeSerializer, CutSerializer, StorySerializer, WebtoonSerializer
from library.models import UserViewedEpisode, Bookmark

class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request): return

class WebtoonListView(generics.ListAPIView):
    queryset = Webtoon.objects.all()
    serializer_class = WebtoonSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        if request.user.is_authenticated:
            # 해당 유저가 본 웹툰 ID 목록만 딱 가져옴
            viewed_ids = UserViewedEpisode.objects.filter(
                user=request.user
            ).values_list('episode__webtoon_id', flat=True).distinct()
            
            for item in data:
                # DB에 기록이 있는 웹툰(역)만 True, 없으면 False
                item['is_viewed'] = item['webtoon_id'] in viewed_ids
        else:
            for item in data:
                item['is_viewed'] = False

        return Response(data)

# ✅ 1. 에피소드 상세 API (초록색 배지 해결사)
class EpisodeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        episode_id = self.request.query_params.get('episode_id')
        episode = get_object_or_404(Episode, episode_id=episode_id)
        
        # 1. 과거 기록 확인 (초록색 배지 결정자)
        is_already_viewed = False
        if request.user.is_authenticated:
            is_already_viewed = UserViewedEpisode.objects.filter(
                user=request.user, episode=episode
            ).exists()
            
            # 기록 업데이트 (다음 방문을 위해)
            UserViewedEpisode.objects.update_or_create(
                user=request.user, 
                episode=episode, 
                defaults={'viewed_at': timezone.now()}
            )

        # 2. 에피소드 기본 정보 직렬화
        episode_data = self.get_serializer(episode).data
        episode_data['is_viewed'] = is_already_viewed # ✅ 정확한 위치에 주입

        # 3. 컷(사진) 데이터 별도 추출 (리액트의 cuts 상태용)
        # ✅ 사진이 안 보였던 이유: 리액트가 data.cuts를 찾는데 백엔드가 안 주고 있었음
        from .serializers import CutSerializer
        cuts_qs = episode.cuts.all().order_by('cut_order')
        cuts_data = CutSerializer(cuts_qs, many=True).data

        print(f"[DEBUG] 응답 전송 - 에피소드:{episode_id}, 사진:{len(cuts_data)}장, 읽음:{is_already_viewed}")

        # 4. 리액트 StoryScreen의 data 구조에 100% 맞춤 응답
        return Response({
            "success": True,
            "episode": episode_data,
            "cuts": cuts_data, # ✅ 리액트 setCuts((data.cuts ?? [])로 들어감
            "is_bookmarked": Bookmark.objects.filter(user=request.user, episode=episode).exists() if request.user.is_authenticated else False
        })

# ✅ 2. 스테이션 스토리 뷰 (랜덤 로직)
class StationStoryView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, station_identifier):
        decoded_name = unquote(station_identifier)
        try:
            episodes = Episode.objects.filter(webtoon__station_id=decoded_name) if decoded_name.isdigit() else Episode.objects.all()
            episode = episodes.order_by('?').first()
            if not episode: return Response({"message": "데이터가 없습니다."}, status=404)
            return Response(StorySerializer(episode).data)
        except Exception as e: return Response({"error": str(e)}, status=500)

# ✅ 3. 에피소드 컷 리스트
class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]
    def get_queryset(self): return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")
    def perform_create(self, serializer): serializer.save(episode_id=self.kwargs["episode_id"])

# ✅ 4. 북마크 토글 API (리액트용)
@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def toggle_bookmark_api(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    with transaction.atomic():
        qs = Bookmark.objects.filter(user=request.user, episode=episode)
        is_bookmarked = not qs.exists()
        if not is_bookmarked: qs.delete()
        else: Bookmark.objects.create(user=request.user, episode=episode)
    return Response({"success": True, "is_bookmarked": is_bookmarked})

# ✅ 5. HTML용 뷰 및 토글 (필요시 사용)
def episode_detail(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    return render(request, 'stories/episode_detail.html', {'episode': episode})

@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    bm, cr = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not cr: bm.delete()
    return redirect('episode_detail', episode_id=episode_id)
