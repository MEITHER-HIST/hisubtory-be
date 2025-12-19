from django.contrib import admin
from .models import Episode

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'episode_num', 'subtitle', 'last_viewed_at')
    list_filter = ('station',)
    search_fields = ('station__station_name', 'subtitle')