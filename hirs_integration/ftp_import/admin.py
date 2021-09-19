from django.contrib import admin
from .models import FileTrack

@admin.register(FileTrack)
class FileTrackAdmin(admin.ModelAdmin):
    pass
