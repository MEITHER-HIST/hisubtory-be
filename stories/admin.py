from django.contrib import admin
from .models import Webtoon, Episode, Cut


@admin.register(Webtoon)
class WebtoonAdmin(admin.ModelAdmin):
    list_display = ("webtoon_id", "station", "title", "author", "created_at")
    search_fields = ("title", "author")
    list_filter = ("station",)

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("episode_id", "webtoon", "episode_num", "is_published", "published_at", "created_at")
    list_filter = ("is_published", "webtoon")
    search_fields = ("subtitle", "history_summary", "source_url")
    ordering = ("-created_at",)


# Cut 모델 Inline 등록
class CutInline(admin.TabularInline):
    model = Cut
    extra = 1  # 새 컷 추가 시 빈 칸 1개
    fields = ('image', 'caption', 'order')  # 입력 필드
    readonly_fields = ()

@admin.register(Cut)
class CutAdmin(admin.ModelAdmin):
    list_display = ("cut_id", "episode", "cut_order", "created_at")
    list_filter = ("cut_order",)
    ordering = ("episode", "cut_order")
