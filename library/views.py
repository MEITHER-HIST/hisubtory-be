# library/views.py

from __future__ import annotations

from typing import Any, Dict

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication

from .models import UserViewedEpisode, Bookmark


# ✅ CSRF 검사를 건너뛰는 세션 인증 클래스 (개발/테스트용)
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


def _safe_thumbnail_url(webtoon: Any) -> str:
    if not webtoon:
        return ""

    thumb = getattr(webtoon, "thumbnail", None)
    if not thumb:
        return ""

    # FileField/ImageField 케이스
    try:
        if hasattr(thumb, "url"):
            return thumb.url or ""
    except Exception:
        return ""

    # 문자열로 저장된 케이스(혹시나)
    if isinstance(thumb, str):
        return thumb

    return ""


def _make_item_from_episode(episode: Any) -> Dict[str, Any]:
    webtoon = getattr(episode, "webtoon", None)
    station = getattr(webtoon, "station", None) if webtoon else None

    return {
        "id": _safe_episode_id(episode),
        "title": getattr(webtoon, "title", "") if webtoon else "",
        "stationName": getattr(station, "station_name", "") if station else "",
        "imageUrl": _safe_thumbnail_url(webtoon),
        "content": getattr(episode, "subtitle", "") or "",
    }


@api_view(["GET"])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_history_api(request):
    user = getattr(request, "user", None)

    # permission_classes가 막아주지만, 응답을 더 명확히 하려고 한 번 더 방어
    if not getattr(user, "is_authenticated", False):
        return Response(
            {"detail": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

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
        for v in viewed_qs
        if getattr(v, "episode", None) is not None
    ]

    saved_data = [
        _make_item_from_episode(b.episode)
        for b in bookmark_qs
        if getattr(b, "episode", None) is not None
    ]

    return Response(
        {"recent": recent_data, "saved": saved_data},
        status=status.HTTP_200_OK,
    )
