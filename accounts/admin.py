from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 커스텀 유저 모델 등록
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Admin 목록 화면에서 보여줄 항목들
    list_display = ('username', 'email', 'nickname', 'is_staff')
    
    # 상세 수정 화면에서 nickname 필드 추가
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname',)}),
    )
    
    # 사용자 추가 화면에서도 nickname 필드 추가
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('nickname',)}),
    )