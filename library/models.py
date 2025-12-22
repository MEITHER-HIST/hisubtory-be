from django.db import models
from django.conf import settings
from stories.models import Episode

# 이미지 생성 API 구성 모델
class UserViewedEpisode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewed_episodes')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'episode')

    def __str__(self):
        return f"{self.user.username} - {self.episode.title}"

# 최근 이야기, 이야기 저장하기 구성 모델
class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    is_saved = models.BooleanField(default=False)  # '이야기 저장하기' 클릭 여부
    last_viewed_at = models.DateTimeField(auto_now=True) # 사용자가 마지막으로 본 시간

    class Meta:
        unique_together = ('user', 'episode') # 중복 기록 방지
        ordering = ['-last_viewed_at'] # 최근에 본 순서대로 정렬