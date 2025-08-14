# transcriber/admin.py

from django.contrib import admin
from .models import AudioTranscription

# Register your models here.
admin.site.register(AudioTranscription)