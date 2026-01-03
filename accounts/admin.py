from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OAuthAccount

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 어드민 목록에 보일 필드 설정
    list_display = ('username', 'email', 'is_staff', 'created_at')
    # 상세 페이지에서 수정 가능한 필드 세트
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(OAuthAccount)