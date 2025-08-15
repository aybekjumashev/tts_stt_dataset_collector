# transcriber/models.py

import os
from django.db import models

class Speaker(models.Model):
    """
    Model to store speaker information.
    """
    code = models.CharField(max_length=20, unique=True, help_text="Unique code for the speaker, e.g., 'speaker_01'")
    name = models.CharField(max_length=100, help_text="Full name of the speaker")

    def __str__(self):
        return f"{self.name} ({self.code})"

class AudioTranscription(models.Model):
    """
    Model to store an audio file and its transcription.
    """
    audio_file = models.FileField(upload_to='wavs/')
    transcription_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT, related_name='audios')
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        # Return the file name for a more readable representation in the admin panel
        return os.path.basename(self.audio_file.name)
    
    @property
    def file_name(self):
        # A property to easily get just the filename
        return os.path.basename(self.audio_file.name)