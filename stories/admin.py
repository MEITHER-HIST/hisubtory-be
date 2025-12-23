from django.contrib import admin
from .models import Episode, Cut

# Cut 모델 Inline 등록
class CutInline(admin.TabularInline):
    model = Cut
    extra = 1  # 새 컷 추가 시 빈 칸 1개
    fields = ('image', 'caption', 'order')  # 입력 필드
    readonly_fields = ()

# EpisodeAdmin 수정
@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('station', 'title', 'image')
    fields = ('station', 'title', 'image')
    inlines = [CutInline]  # Episode 상세에서 컷 추가 가능
