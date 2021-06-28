from django.db import models

class FileTrack(models.Model):
    """Table to track which files have been imported already"""
    name = models.CharField(max_length=255,unique=True)