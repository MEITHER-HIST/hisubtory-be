from django.contrib import admin
from .models import Story, StationStoryMeta

@admin.register(StationStoryMeta)
class StationStoryMetaAdmin(admin.ModelAdmin):
    list_display = ('station',)

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('station', 'created_at')