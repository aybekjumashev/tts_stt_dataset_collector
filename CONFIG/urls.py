# karakalpak_stt/urls.py

from django.contrib import admin
from django.urls import path, include  # Import include
from django.conf import settings         # Import settings
from django.conf.urls.static import static # Import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transcriber.urls')), 
    # login
    path('accounts/', include('django.contrib.auth.urls')),
]

# Add this line to serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)