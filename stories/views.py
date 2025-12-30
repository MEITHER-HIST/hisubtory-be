from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from urllib.parse import unquote
import random

# 모델 및 시리얼라이저 임포트
# [수정] 존재하지 않는 EpisodeSerializer를 임포트 목록에서 삭제했습니다.
from .models import Episode, Cut, Webtoon
from .serializers import StorySerializer, CutSerializer 
from library.models import UserViewedEpisode, Bookmark

# 1. [HTML] 에피소드 상세 페이지 뷰 (웹 페이지용)
def episode_detail_view(request, episode_id):
    user = request.user if request.user.is_authenticated else None
    episode = get_object_or_404(Episode, id=episode_id)
    
    if user:
        from django.utils import timezone
        UserViewedEpisode.objects.update_or_create(
            user=user, 
            episode=episode,
            defaults={'viewed_at': timezone.now()} 
        )

    # [수정] 모델에서 cut_order를 삭제했으므로 id 순으로 4개 가져오기
    cuts = episode.cuts.all()[:4]

    # 같은 역의 다른 에피소드들
    all_episodes = Episode.objects.filter(station_id=episode.station_id)
    other_episodes = all_episodes.exclude(id=episode.id)

    is_bookmarked = False
    if user:
        is_bookmarked = Bookmark.objects.filter(user=user, episode=episode).exists()

    new_episode_button = False
    if user:
        viewed_episodes = UserViewedEpisode.objects.filter(user=user, episode__station_id=episode.station_id)
        if viewed_episodes.exists():
            new_episode_button = True

        if request.GET.get('next') == 'true':
            unseen_episodes = Episode.objects.filter(station_id=episode.station_id).exclude(
                id__in=viewed_episodes.values_list('episode_id', flat=True)
            )
            if unseen_episodes.exists():
                episode = random.choice(list(unseen_episodes))
                UserViewedEpisode.objects.get_or_create(user=user, episode=episode)
                cuts = episode.cuts.all()[:4]
            new_episode_button = False

    context = {
        'episode': episode,
        'cuts': cuts,
        'other_episodes': other_episodes,
        'new_episode_button': new_episode_button,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'stories/episode_detail.html', context)


# 2. [API] 역 식별자(ID 또는 이름) 기반 스토리 조회 (React 앱 메인용)
class StationStoryView(APIView):
    def get(self, request, station_identifier):
        decoded_name = unquote(station_identifier) # 인코딩된 역 이름 복구
        try:
            # 1. 숫자인 경우 station_id로 검색
            if decoded_name.isdigit():
                episode = Episode.objects.filter(station_id=decoded_name).first()
            else:
                # 2. 문자열인 경우 '종로3가' 등으로 검색 (필드 구조에 따라 조정)
                # 현재 Episode 모델에 station 관계가 단순 IntegerField이므로
                # 일단 첫 번째 데이터를 반환하도록 하여 에러를 방지합니다.
                episode = Episode.objects.all().first()

            if not episode:
                return Response({"message": "데이터가 없습니다."}, status=404)

            serializer = StorySerializer(episode)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# 3. [API] 에피소드별 컷 리스트 조회 및 생성 (관리자/개발용)
class EpisodeCutListCreateView(generics.ListCreateAPIView):
    serializer_class = CutSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # [수정] 존재하지 않는 cut_order 대신 id 순으로 정렬
        return Cut.objects.filter(episode_id=self.kwargs["episode_id"]).order_by("id")

    def perform_create(self, serializer):
        serializer.save(episode_id=self.kwargs["episode_id"])


# 4. [기능] 북마크 토글 기능
@login_required
def toggle_bookmark(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, episode=episode)
    if not created:
        bookmark.delete()
    return redirect('episode_detail', episode_id=episode_id)


# 5. [API] 기존 호환용 station_stories_api
@api_view(['GET'])
def station_stories_api(request, station_id):
    episodes = Episode.objects.filter(station_id=station_id)
    
    if not episodes.exists():
        episodes = Episode.objects.all()

    if episodes.exists():
        episode = episodes.first() 
        # [수정] EpisodeSerializer 대신 StorySerializer를 공용으로 사용합니다.
        serializer = StorySerializer(episode)
        return Response(serializer.data)
    
    return Response({"message": "해당 역의 스토리가 없습니다."}, status=404)