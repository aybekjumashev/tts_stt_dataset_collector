# transcriber/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Map the root URL to our main_view
    path('', views.main_view, name='main_view'),
    path('upload/', views.upload_audio_view, name='upload_audio'),
    path('save-transcription/', views.save_transcription_view, name='save_transcription'),
    path('delete-audio/', views.delete_audio_view, name='delete_audio'),
    path('export/', views.export_dataset_view, name='export_dataset'),
]