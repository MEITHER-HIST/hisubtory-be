from django.db import models
<<<<<<< HEAD
from django.utils import timezone # 추가

class Episode(models.Model):
    station = models.ForeignKey('subway.Station', on_delete=models.CASCADE)
    episode_num = models.IntegerField(default=1)
    title = models.CharField(max_length=200, default='제목 없음') # 기본값 추가
    subtitle = models.CharField(max_length=200, blank=True, null=True, default='')
    history_summary = models.TextField()
    # default=timezone.now 를 추가하여 빈 데이터 문제 해결
    last_viewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('station', 'episode_num')

    def __str__(self):
        return f"[{self.station.name}] {self.title}"

class EpisodeImage(models.Model):
    # related_name='images'를 통해 episode.images.all()로 접근 가능합니다.
    episode = models.ForeignKey(Episode, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='episode_images/')
    caption = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
=======
from subway.models import Station

def episode_upload_to(instance, filename):
    return f'episodes/{filename}'

class Episode(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='기본 제목')
    image = models.ImageField(upload_to=episode_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.station.station_name} - {self.title}"
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
