import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from urllib.parse import unquote

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.views.decorators.csrf import csrf_exempt
from .models import Webtoon, Episode, Cut
from .serializers import EpisodeSerializer, CutSerializer, StorySerializer
from library.models import UserViewedEpisode, Bookmark

# 1. HTML 상세 뷰 (웹용)
def episode_detail(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    cuts = episode.cuts.all().order_by('cut_order')
    
    if request.user.is_authenticated:
        view_record, created = UserViewedEpisode.objects.get_or_create(
            user=request.user, 
            episode=episode
        )
        if not created:
            view_record.viewed_at = timezone.now() 
            view_record.save(update_fields=['viewed_at'])

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

# 2. 리액트 연동 상세 API (is_bookmarked 포함)
class EpisodeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]
    # 세션 인증을 명시하여 리액트에서 보낸 유저 정보를 확인합니다.
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get(self, request, *args, **kwargs):
        episode_id = self.request.query_params.get('episode_id')
        if not episode_id:
            return Response({"success": False, "message": "id missing"}, status=400)
        
        episode = get_object_or_404(Episode, episode_id=episode_id)
        
        # 상세페이지 진입 시 시청 기록 생성/업데이트
        is_bookmarked = False
        if request.user.is_authenticated:
            view_record, created = UserViewedEpisode.objects.get_or_create(
                user=request.user, 
                episode=episode
            )
            if not created:
                view_record.viewed_at = timezone.now()
                view_record.save(update_fields=['viewed_at'])
            
            # 북마크 여부 확인
            is_bookmarked = Bookmark.objects.filter(user=request.user, episode=episode).exists()

        serializer = self.get_serializer(episode)
        return Response({
            "success": True, 
            "episode": serializer.data, 
            "cuts": serializer.data.get('cuts', []),
            "is_bookmarked": is_bookmarked # 리액트 StoryScreen의 setIsSaved용
        })

# 3. StationStoryView
class StationStoryView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, station_identifier):
        decoded_name = unquote(station_identifier)
        try:
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
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("cut_order")
    
    def perform_create(self, serializer):
        serializer.save(episode_id=self.kwargs["episode_id"])

# 5. 북마크 토글 (HTML용)
@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()
    return redirect('episode_detail', episode_id=episode_id)

from django.db import transaction
from rest_framework import status
from rest_framework.authentication import SessionAuthentication

# ✅ CSRF 체크를 하지 않는 커스텀 세션 인증 클래스 (테스트용)
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])  # ✅ CSRF 우회 + 세션 쿠키 읽기
@permission_classes([IsAuthenticated])                  # ✅ 로그인 필수
def toggle_bookmark_api(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    user = request.user

    if not user or not user.is_authenticated:
        return Response(
            {"success": False, "message": "로그인이 필요합니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    with transaction.atomic():
        qs = Bookmark.objects.filter(user=user, episode=episode)
        if qs.exists():
            qs.delete()
            is_bookmarked = False
        else:
            Bookmark.objects.create(user=user, episode=episode)
            is_bookmarked = True

    return Response(
        {
            "success": True,
            "is_bookmarked": is_bookmarked,
            "message": "북마크 상태가 변경되었습니다.",
        },
        status=status.HTTP_200_OK,
    )
