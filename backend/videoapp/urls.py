from django.conf import settings
from django.contrib import admin
from django.templatetags.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('videoprocessing.urls')),
]

