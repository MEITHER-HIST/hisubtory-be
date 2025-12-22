from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
<<<<<<< HEAD
    # 기본 username, password 외에 추가할 필드
    nickname = models.CharField(max_length=50, blank=True)
=======
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

<<<<<<< HEAD

    def __str__(self):
        return self.nickname if self.nickname else self.username
=======
class OAuthAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)  # google, kakao
    provider_user_id = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'provider_user_id')
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
