from django.contrib import admin
from .models import Station, Line
# from .models import StationLine

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("station_name", "station_code", "is_enabled")
    search_fields = ("station_name", "station_code")
    list_filter = ("is_enabled",)

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ("line_name", "line_color", "created_at")
    search_fields = ("line_name",)
# admin.site.register(StationLine)