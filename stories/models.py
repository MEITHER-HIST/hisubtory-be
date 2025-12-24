from django.db import models
from subway.models import Station

# =========================
# 1) 역별 시리즈(Webtoon)
# =========================
class Webtoon(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='webtoons')
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='webtoons/', blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.station.station_name} - {self.title}"


# =========================
# 2) Episode
# =========================
class Episode(models.Model):
    webtoon = models.ForeignKey(Webtoon, on_delete=models.CASCADE, related_name='episodes', null=True, blank=True)  # nullable/blank 허용
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)  # 직접 FK 추가
    episode_num = models.IntegerField()
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    story_text = models.TextField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('webtoon', 'episode_num')
        ordering = ['webtoon', 'episode_num']

    def __str__(self):
        return f"{self.webtoon.title if self.webtoon else 'No Webtoon'} - {self.episode_num}화"


# =========================
# 3) 4컷 이미지 (Cut)
# =========================
class Cut(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='cuts')
    image = models.ImageField(upload_to='episode_cuts/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        # unique_together 제거 → 중복 가능

    def __str__(self):
        return f"{self.episode} - 컷 {self.order + 1}"
