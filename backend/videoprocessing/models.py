
from django.db import models
from django.utils import timezone

class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

class Subtitle(models.Model):
    video_file_name = models.CharField(max_length=10, blank=True, null=True)
    language_code = models.CharField(max_length=10)
    subtitle_type = models.CharField(max_length=10, choices=[('extracted', 'Extracted'), ('generated', 'Generated')], blank=True, null=True)
    subtitle_file = models.BinaryField()
    subtitle_name_ext = models.CharField(max_length=200,blank=True, null=True)
    file_format = models.CharField(max_length=10, blank=True, null=True)  # Allow null values
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video_file_name} - {self.language_code}"


