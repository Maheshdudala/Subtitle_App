from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (UploadVideoView, SearchSubtitlesView, ListVideosView, VideoDetailView, GetSubtitleView)

urlpatterns = [
    path('upload/', UploadVideoView.as_view(), name='upload_video'),
    path('search_subtitles/', SearchSubtitlesView.as_view(), name='search_subtitles'),
    path('list-videos/', ListVideosView.as_view(), name='list-videos'),
    path('video-detail/', VideoDetailView.as_view(), name='video-detail'),
    path('get_subtitle/<int:subtitle_id>/', GetSubtitleView.as_view(), name='get_subtitle'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
