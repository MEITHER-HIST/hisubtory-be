from django.db import models
from subway.models import Station

class Episode(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='기본 제목')
    image = models.ImageField(upload_to='episodes/')

    def __str__(self):
        return f"{self.station.name} - {self.title}"