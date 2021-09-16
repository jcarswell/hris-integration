from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class FileTrackAdmin(admin.ModelAdmin):
    pass
