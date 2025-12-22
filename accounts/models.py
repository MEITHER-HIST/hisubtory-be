from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 기본 username, password 외에 추가할 필드
    nickname = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.nickname if self.nickname else self.username