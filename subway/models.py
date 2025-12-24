from django.db import models

class Line(models.Model):
    line_name = models.CharField(max_length=50, unique=True)
    line_color = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.line_name

class Station(models.Model):
    station_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    station_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_enabled = models.BooleanField(default=False)  # 추가
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='stations/', null=True, blank=True)

    def __str__(self):
        return self.station_name

class StationLine(models.Model):
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    station_order = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('line', 'station')

    def __str__(self):
        return f"{self.line} - {self.station}" 