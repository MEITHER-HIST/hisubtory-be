from django.db import models
from django.utils import timezone
from subway.models import Station 

class Episode(models.Model):
    # Station 모델을 직접 참조
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='episodes')
    episode_num = models.IntegerField()
    subtitle = models.CharField(max_length=255)  # AI 프롬프트 키워드
    history_summary = models.TextField()       # 하단 자막/설명
    
    # 이미지 파일 저장 필드 (Pillow 설치 필수)
    source_url = models.ImageField(upload_to='episodes/%Y/%m/', null=True, blank=True)
    
    # 순환 노출 및 생성 기록 필드
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 특정 역 내에서 에피소드 번호 중복 방지
        unique_together = ('station', 'episode_num')

    def __str__(self):
        return f"[{self.station.name}] Ep.{self.episode_num} - {self.subtitle}"