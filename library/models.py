from django.db import models
from django.conf import settings
from stories.models import Episode

User = settings.AUTH_USER_MODEL

# --- 사용자가 본 에피소드 기록 ---
class UserViewedEpisode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_episodes')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'episode')

    def __str__(self):
        return f"{self.user} - {self.episode.title}"


# --- 북마크 모델 ---
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'episode')

    def __str__(self):
        return f"{self.user} - 북마크: {self.episode.title}"
