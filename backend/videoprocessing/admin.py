from django.contrib import admin
from .models import Subtitle

@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'video_file_name', 'language_code', 'subtitle_type', 'subtitle_file','subtitle_name_ext','file_format', 'created_at' )