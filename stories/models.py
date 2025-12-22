from django.db import models
from subway.models import Station

def episode_upload_to(instance, filename):
    return f'episodes/{filename}'

class Episode(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='기본 제목')
    image = models.ImageField(upload_to=episode_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.station.station_name} - {self.title}"