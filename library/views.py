from __future__ import annotations
from typing import Any, Dict
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from .models import UserViewedEpisode, Bookmark

# CSRF 검사를 건너뛰는 세션 인증 클래스
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

def _safe_episode_id(episode: Any) -> str:
    return str(
        getattr(
            episode,
            "episode_id",
            getattr(episode, "id", getattr(episode, "pk", "")),
        )
    )

import urllib.parse

def _safe_thumbnail_url(webtoon: Any) -> str:
    if not webtoon:
        return ""

    thumb = getattr(webtoon, "thumbnail", None)
    if not thumb:
        return ""

    try:
        # 1. 원본 URL 추출
        url = ""
        if hasattr(thumb, "url"):
            url = thumb.url or ""
        elif isinstance(thumb, str):
            url = thumb

        # 2. URL 디코딩 (%3A -> :, %2F -> / 복구)
        url = urllib.parse.unquote(url)

        # 3. [핵심 로직] 이미 전체 경로(http)가 포함된 경우 처리
        if 'http' in url:
            # /media/http... 처럼 앞에 미디어 경로가 붙어있다면 뒤쪽 http부터 잘라냄
            if '/media/http' in url:
                url = 'http' + url.split('/media/http')[-1]
            # 혹은 이미 깨끗한 전체 주소라면 그대로 유지됨
            return url

        return url
    except Exception:
        return ""

def _make_item_from_episode(episode: Any) -> Dict[str, Any]:
    webtoon = getattr(episode, "webtoon", None)
    station = getattr(webtoon, "station", None) if webtoon else None
    return {
        "id": _safe_episode_id(episode),
        "title": getattr(episode, "subtitle", "") or f"{getattr(webtoon, 'title', '')} 에피소드",
        "stationName": getattr(station, "station_name", "알 수 없는 역") if station else "알 수 없는 역",
        "imageUrl": _safe_thumbnail_url(webtoon),
        "content": f"{getattr(webtoon, 'title', '웹툰')}의 이야기입니다.",
    }

@api_view(["GET"])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_history_api(request):
    """최근 본 기록 10개와 내 이야기(북마크) 데이터를 반환"""
    user = request.user

    # 1) 최근 본 이야기 10개
    viewed_qs = (
        UserViewedEpisode.objects.filter(user=user)
        .select_related("episode__webtoon__station")
        .order_by("-viewed_at")[:10]
    )

    # 2) 저장한 이야기(북마크)
    bookmark_qs = (
        Bookmark.objects.filter(user=user)
        .select_related("episode__webtoon__station")
        .order_by("-created_at")
    )

    recent_data = [
        _make_item_from_episode(v.episode)
        for v in viewed_qs if getattr(v, "episode", None)
    ]

    saved_data = [
        _make_item_from_episode(b.episode)
        for b in bookmark_qs if getattr(b, "episode", None)
    ]

    return Response(
        {"recent": recent_data, "saved": saved_data},
        status=status.HTTP_200_OK,
    )