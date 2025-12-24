from django.db import models
from django.conf import settings
from stories.models import Episode
from subway.models import Station

User = settings.AUTH_USER_MODEL

# --- 사용자가 본 에피소드 기록 + 저장 기능 통합 ---
class UserViewedEpisode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_episodes')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, default=1)  # 역 단위 조회 최적화
    viewed_at = models.DateTimeField(auto_now_add=True)

    # 저장(북마크) 기능
    saved = models.BooleanField(default=False)
    saved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'episode')
        indexes = [
            models.Index(fields=['user', 'episode']),           # 기본 PK 용도
            models.Index(fields=['user', 'station']),           # "이 역 콘텐츠 봤는지" 조회용
            models.Index(fields=['user', 'saved', 'station']),  # 저장/북마크 조회용
            models.Index(fields=['user', 'viewed_at']),         # 최근 본 목록 조회용
        ]

    def __str__(self):
        return f"{self.user} - {self.episode.title} (saved={self.saved})"
