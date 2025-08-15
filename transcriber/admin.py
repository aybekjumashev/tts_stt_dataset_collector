from django.contrib import admin
from .models import AudioTranscription, Speaker

class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

class AudioTranscriptionAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'speaker', 'created_at')
    list_filter = ('speaker',)
    search_fields = ('audio_file',)

admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(AudioTranscription, AudioTranscriptionAdmin)