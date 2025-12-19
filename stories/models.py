from django.db import models
from subway.models import Station

class Episode(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='기본 제목')
    image = models.ImageField(upload_to='episodes/')

    def __str__(self):
        return f"{self.station.name} - {self.title}"
    
    # 기획자가 미리 입력하는 키워드/캡션
class StationStoryMeta(models.Model):
    station = models.OneToOneField(Station, on_delete=models.CASCADE)
    kw_1 = models.CharField(max_length=255); cp_1 = models.TextField()
    kw_2 = models.CharField(max_length=255); cp_2 = models.TextField()
    kw_3 = models.CharField(max_length=255); cp_3 = models.TextField()
    kw_4 = models.CharField(max_length=255); cp_4 = models.TextField()

# AI가 생성한 실제 이미지 결과물
class Story(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    image_1 = models.ImageField(upload_to='stories/%Y/%m/')
    caption_1 = models.TextField()
    # ... image_4, caption_4까지 동일하게 구성