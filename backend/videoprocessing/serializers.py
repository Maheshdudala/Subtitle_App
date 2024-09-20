# videoprocessing/serializers.py
from rest_framework import serializers
from .models import Video, Subtitle

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'file', 'created_at']

