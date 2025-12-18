from django.db import models
from django.conf import settings
from stories.models import Episode

class UserViewedEpisode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewed_episodes')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'episode')

    def __str__(self):
        return f"{self.user.username} - {self.episode.title}"