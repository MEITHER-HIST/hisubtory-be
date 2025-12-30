# stories/models.py
import os, uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from subway.models import Station

def episode_upload_to(instance, filename):
    return f"episodes/{filename}"

def thumbnail_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"webtoons/station_{instance.station_id}/thumb_{uuid.uuid4().hex}{ext}"

def cut_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    # episode/webtoon/station 기준으로 폴더 정리 + 파일명 유니크
    st_id = instance.episode.webtoon.station_id
    wt_id = instance.episode.webtoon_id
    ep_num = instance.episode.episode_num
    order = instance.cut_order
    return f"webtoons/station_{st_id}/webtoon_{wt_id}/ep_{ep_num}/cut_{order}_{uuid.uuid4().hex}{ext}"

class Webtoon(models.Model):
    webtoon_id = models.BigAutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=200)          # "OO역 히서터리"
    author = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_to, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "webtoons"

    def __str__(self):
        return f"[{self.station_id}] {self.title}"

class Episode(models.Model):
    episode_id = models.BigAutoField(primary_key=True)
    webtoon = models.ForeignKey(Webtoon, on_delete=models.CASCADE, null=True, blank=True, related_name="episodes")
    episode_num = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    history_summary = models.TextField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "episodes"
        constraints = [
            models.UniqueConstraint(fields=["webtoon", "episode_num"], name="uniq_webtoon_episode_num"),
        ]
        indexes = [
            models.Index(fields=["webtoon", "episode_num"]),
            models.Index(fields=["is_published", "published_at"]),
        ]

    def __str__(self):
        return f"Webtoon#{self.webtoon_id} - EP{self.episode_num}"

class Cut(models.Model):
    cut_id = models.BigAutoField(primary_key=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="cuts")
    cut_order = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )  # 1~4
    image = models.ImageField(upload_to=cut_upload_to)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cuts"
        constraints = [
            models.UniqueConstraint(fields=["episode", "cut_order"], name="uniq_episode_cut_order"),
        ]
        indexes = [
            models.Index(fields=["episode", "cut_order"]),
        ]
        ordering = ["cut_order"]

    def __str__(self):
        return f"EP#{self.episode_id} CUT{self.cut_order}"
