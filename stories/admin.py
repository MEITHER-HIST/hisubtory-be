from django.contrib import admin
from .models import Episode, EpisodeImage

class EpisodeImageInline(admin.TabularInline):
    model = EpisodeImage
    extra = 0

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'episode_num', 'title')
    inlines = [EpisodeImageInline]