# transcriber/models.py

import os
from django.db import models

class AudioTranscription(models.Model):
    """
    Model to store an audio file and its transcription.
    """
    audio_file = models.FileField(upload_to='wavs/')
    transcription_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return the file name for a more readable representation in the admin panel
        return os.path.basename(self.audio_file.name)
    
    @property
    def file_name(self):
        # A property to easily get just the filename
        return os.path.basename(self.audio_file.name)