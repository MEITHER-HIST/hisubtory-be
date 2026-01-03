from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User, OAuthAccount, MembershipRequest, Team, TeamMember

# --- [1] 커스텀 유저 관리 ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 목록 화면 구성
    list_display = ('username', 'email', 'is_leader_approved', 'leader_code', 'is_staff')
    list_filter = ('is_leader_approved', 'is_staff', 'is_superuser')
    
    # 상세 수정 페이지 구성
    fieldsets = UserAdmin.fieldsets + (
        ('팀장 권한 관리', {'fields': ('is_leader_approved', 'leader_code')}),
    )
    
    # 유저 생성 페이지 구성 (이 부분이 빠지면 유저 생성 시 오류가 날 수 있음)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('팀장 권한 관리', {'fields': ('is_leader_approved', 'leader_code')}),
    )

# --- [2] 신청 현황 관리 (핵심 로직) ---
@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'request_type', 'team_name', 'status', 'created_at']
    list_filter = ['status', 'request_type']
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description="선택된 항목 승인 (팀장/팀원 자동 처리)")
    def approve_requests(self, request, queryset):
        leader_count = 0
        member_count = 0
        
        for req in queryset:
            if req.status == 'PENDING':
                # 1. 팀장 신청 승인 처리
                if req.request_type == 'LEADER':
                    req.user.approve_as_leader(req.team_name)
                    req.status = 'APPROVED'
                    req.save()
                    leader_count += 1
                
                # 2. 팀원 신청 승인 처리 (이 부분이 추가되었습니다)
                elif req.request_type == 'MEMBER':
                    from .models import Team, TeamMember
                    # 팀 코드로 해당 팀을 찾음
                    try:
                        team = Team.objects.get(team_code=req.target_leader_code)
                        TeamMember.objects.get_or_create(team=team, user=req.user)
                        req.status = 'APPROVED'
                        req.save()
                        member_count += 1
                    except Team.DoesNotExist:
                        # 팀을 찾을 수 없는 경우 예외 처리
                        pass
        
        self.message_user(request, f"승인 완료: 팀장 {leader_count}건, 팀원 {member_count}건이 처리되었습니다.")

# --- [3] 팀 및 팀원 관리 ---
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'team_code', 'created_at') # team_code 추가
    search_fields = ('name', 'leader__username', 'team_code')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'user', 'joined_at')
    list_filter = ('team',)

@admin.register(OAuthAccount)
class OAuthAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'email', 'created_at')