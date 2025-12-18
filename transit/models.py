from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=100)
    line = models.CharField(max_length=10, default='3호선')       # 1호선~9호선
    is_enabled = models.BooleanField(default=False)  # 오픈 여부

    def __str__(self):
        return f"{self.line} - {self.name}"