# stories/models.py
import os, uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from subway.models import Station

def cut_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    # instance.episode.id를 직접 사용하여 경로 생성
    return f"webtoons/station_{instance.episode.station_id}/ep_{instance.episode.id}/cut_{instance.cut_order}_{uuid.uuid4().hex}{ext}"

class Webtoon(models.Model):
    webtoon_id = models.BigAutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="webtoons/thumbnails/", blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "webtoons"

    def __str__(self):
        return self.title

# stories/models.py

class Episode(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ForeignKey 대신 숫자로 직접 매핑 (가장 안전)
    station_id = models.IntegerField(db_column='station_id') 
    title = models.CharField(max_length=200)
    episode_num = models.IntegerField()
    subtitle = models.CharField(max_length=255)
    history_summary = models.TextField()
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    source_url = models.URLField(blank=True, null=True, db_column='source_url')

    class Meta:
        db_table = "stories_episode"
        managed = False # 기존 DB를 건드리지 않음

class Cut(models.Model):
    id = models.BigAutoField(primary_key=True)
    # episode_id 컬럼과 직접 매핑
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="cuts", db_column='episode_id')
    image = models.CharField(max_length=255, db_column='image') # ImageField 대신 CharField로 경로만 읽기
    caption = models.CharField(max_length=500, db_column='caption')

    class Meta:
        db_table = "stories_episodeimage"
        managed = False