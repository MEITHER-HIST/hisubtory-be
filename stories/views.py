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
from .serializers import EpisodeSerializer, CutSerializer, StorySerializer
from library.models import UserViewedEpisode, Bookmark

# ✅ CSRF 체크를 하지 않는 커스텀 세션 인증 클래스
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

# 1. HTML 상세 뷰 (웹용)
def episode_detail(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    cuts = episode.cuts.all().order_by('cut_order')
    
    if request.user.is_authenticated:
        try:
            view_record, created = UserViewedEpisode.objects.get_or_create(
                user=request.user, 
                episode=episode
            )
            if not created:
                view_record.viewed_at = timezone.now() 
                view_record.save(update_fields=['viewed_at'])
        except IntegrityError:
            pass

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
        'station_name': episode.webtoon.station.station_name, 
    }
    return render(request, 'stories/episode_detail.html', context)

# 2. 리액트 연동 상세 API
class EpisodeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]
    authentication_classes = [UnsafeSessionAuthentication, BasicAuthentication]

    def get(self, request, *args, **kwargs):
        episode_id = self.request.query_params.get('episode_id')
        if not episode_id:
            return Response({"success": False, "message": "id missing"}, status=400)
        
        episode = get_object_or_404(Episode, episode_id=episode_id)
        is_bookmarked = False
        
        if request.user.is_authenticated:
            try:
                view_record, created = UserViewedEpisode.objects.get_or_create(
                    user=request.user, 
                    episode=episode
                )
                if not created:
                    view_record.viewed_at = timezone.now()
                    view_record.save(update_fields=['viewed_at'])
                
                is_bookmarked = Bookmark.objects.filter(user=request.user, episode=episode).exists()
            except IntegrityError:
                is_bookmarked = False

        serializer = self.get_serializer(episode)
        return Response({
            "success": True, 
            "episode": serializer.data, 
            "cuts": serializer.data.get('cuts', []),
            "is_bookmarked": is_bookmarked
        })

# 3. StationStoryView (랜덤 로직 강화)
class StationStoryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, station_identifier):
        decoded_name = unquote(station_identifier)
        try:
            if decoded_name.isdigit():
                episodes = Episode.objects.filter(webtoon__station_id=decoded_name)
            else:
                episodes = Episode.objects.all()
                
            episode = episodes.order_by('?').first() # 🎲 랜덤 선택
                
            if not episode:
                return Response({"message": "데이터가 없습니다."}, status=404)
                
            serializer = StorySerializer(episode)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# 4. 에피소드별 컷 관리 API
class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")
    
    def perform_create(self, serializer):
        serializer.save(episode_id=self.kwargs["episode_id"])

# 5. 북마크 토글 (HTML용 - 에러 해결을 위해 복구)
@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()
    return redirect('episode_detail', episode_id=episode_id)

# 6. 북마크 토글 API (리액트용)
@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def toggle_bookmark_api(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    user = request.user

    with transaction.atomic():
        qs = Bookmark.objects.filter(user=user, episode=episode)
        if qs.exists():
            qs.delete()
            is_bookmarked = False
        else:
            Bookmark.objects.create(user=user, episode=episode)
            is_bookmarked = True

    return Response({
        "success": True,
        "is_bookmarked": is_bookmarked,
        "message": "북마크 상태가 변경되었습니다.",
    }, status=status.HTTP_200_OK)