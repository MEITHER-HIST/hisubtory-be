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
    # 중복 정의되었던 reject_requests를 정리하고 하나로 합쳤습니다.
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description="선택된 항목 승인 (팀 자동 생성)")
    def approve_requests(self, request, queryset):
        count = 0
        for req in queryset:
            if req.status == 'PENDING':
                if req.request_type == 'LEADER':
                    # User 모델의 approve_as_leader 메서드 호출
                    req.user.approve_as_leader(req.team_name)
                    req.status = 'APPROVED'
                    req.save()
                    count += 1
                elif req.request_type == 'MEMBER':
                    # 팀원 신청은 팀장이 처리하는 것이 원칙이지만, 
                    # 관리자가 강제 승인할 경우 TeamMember에 추가 로직 구현 가능
                    pass
        self.message_user(request, f"{count}건의 팀장 신청이 승인되어 팀 코드가 발급되었습니다.")

    @admin.action(description="선택된 항목 반려")
    def reject_requests(self, request, queryset):
        updated_count = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f"{updated_count}건의 신청이 반려되었습니다.")

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