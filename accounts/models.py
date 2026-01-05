from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ✅ 팀장 승인 관련 필드
    is_leader_approved = models.BooleanField(default=False)
    leader_code = models.CharField(max_length=20, blank=True, null=True)

    def approve_as_leader(self, team_name):
        """이 메서드가 실행되어야 번호가 생성됩니다."""
        if not self.leader_code:
            # 8자리의 고유한 팀 코드 생성
            self.leader_code = str(uuid.uuid4()).upper()[:8]
        
        self.is_leader_approved = True
        self.save()
        
        # 실제 Team 객체 생성 (이미 존재하면 가져옴)
        from .models import Team # 순환 참조 방지용 내부 임포트
        team, created = Team.objects.get_or_create(
            leader=self,
            defaults={'name': team_name, 'team_code': self.leader_code}
        )
        return team
    
    class Meta:
        db_table = 'users'
        

class Team(models.Model):
    """승인된 팀장들이 소유하는 팀 정보"""
    name = models.CharField(max_length=100, unique=True, verbose_name="팀명")
    leader = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_managed_team')
    # 팀원 가입용 고유 코드 (팀장의 leader_code와 동일하게 관리하거나 별도 생성)
    team_code = models.CharField(max_length=20, unique=True, verbose_name="팀 고유번호", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 팀 생성 시 팀장의 leader_code를 팀 코드로 동기화
        if not self.team_code and self.leader.leader_code:
            self.team_code = self.leader.leader_code
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'teams'

class TeamMember(models.Model):
    """팀에 소속된 실제 팀원들 (북마크 공유 대상자)"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='joined_teams')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'team_members'
        unique_together = ('team', 'user')

class MembershipRequest(models.Model):
    """마이페이지에서 발생하는 팀장/팀원 신청 기록"""
    TYPE_CHOICES = [('LEADER', '팀장 신청'), ('MEMBER', '팀원 신청')]
    STATUS_CHOICES = [('PENDING', '대기'), ('APPROVED', '승인'), ('REJECTED', '반려')]

    request_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_requests')
    
    applicant_name = models.CharField(max_length=50, verbose_name="신청자명")
    team_name = models.CharField(max_length=100, verbose_name="팀명")
    target_leader_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="팀 고유번호")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'membership_requests'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['target_leader_code']),
        ]

class OAuthAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    provider_user_id = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'provider_user_id')
        db_table = 'oauth_accounts'