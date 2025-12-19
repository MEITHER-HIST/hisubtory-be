from django.db import models
from django.utils import timezone
from subway.models import Station


class Episode(models.Model):
    # webtoons를 삭제하고 station과 직접 연결
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='episodes')
    episode_num = models.IntegerField()
    subtitle = models.CharField(max_length=255)  # AI 이미지 생성 키워드
    history_summary = models.TextField()       # 텍스트 설명
    
    # ERD의 source_url 대응 (이미지 파일 저장)
    source_url = models.ImageField(upload_to='episodes/%Y/%m/', null=True, blank=True)
    
    # 순환 노출 알고리즘을 위한 필드
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 역 안에서 에피소드 번호 중복 방지
        unique_together = ('station', 'episode_num')

    def __str__(self):
        return f"[{self.station.station_name}] Ep.{self.episode_num}"