# transcriber/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import AudioTranscription
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
import json
import io
import zipfile
import csv 
from django.db.models import Q
from django.core.paginator import Paginator

def main_view(request):
    """
    Display the main page with filtering, search, pagination, and statistics.
    """
    total_audios = AudioTranscription.objects.count()
    with_transcription_count = AudioTranscription.objects.exclude(Q(transcription_text__isnull=True) | Q(transcription_text__exact='')).count()
    without_transcription_count = total_audios - with_transcription_count

    queryset = AudioTranscription.objects.all().order_by('created_at')

    filter_by = request.GET.get('filter_by', 'all')
    if filter_by == 'with_transcription':
        queryset = queryset.exclude(Q(transcription_text__isnull=True) | Q(transcription_text__exact=''))
    elif filter_by == 'without_transcription':
        queryset = queryset.filter(Q(transcription_text__isnull=True) | Q(transcription_text__exact=''))

    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(transcription_text__icontains=search_query)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_by': filter_by,
        'q': search_query,
        'stats': {
            'total': total_audios,
            'with_transcription': with_transcription_count,
            'without_transcription': without_transcription_count,
        }
    }
    return render(request, 'index.html', context)



@require_POST 
def upload_audio_view(request):
    """
    View to handle the upload of multiple .wav files.
    """
    uploaded_files = request.FILES.getlist('audio_files')
    
    for file in uploaded_files:
        if file.name.endswith('.wav'):
            AudioTranscription.objects.create(audio_file=file)
            
    return redirect('main_view')



@require_POST
def save_transcription_view(request):
    """
    View to save the transcription text for a given audio file via AJAX.
    """
    try:
        data = json.loads(request.body)
        audio_id = data.get('audio_id')
        transcription = data.get('transcription')

        audio_transcription = get_object_or_404(AudioTranscription, pk=audio_id)
        audio_transcription.transcription_text = transcription
        audio_transcription.save()

        return JsonResponse({'status': 'success', 'message': 'Transcription saved!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
def export_dataset_view(request):
    """
    View to generate and serve the dataset as a zip file using the correct CSV format.
    """
    records = AudioTranscription.objects.exclude(
        Q(transcription_text__isnull=True) | Q(transcription_text__exact='')
    ).order_by('created_at')
    string_buffer = io.StringIO()
    
    csv_writer = csv.writer(string_buffer, quoting=csv.QUOTE_MINIMAL)

    for record in records:
        transcription = record.transcription_text or ''
        csv_writer.writerow([record.file_name, transcription])

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('dataset/metadata.csv', string_buffer.getvalue().encode('utf-8'))
        
        for record in records:
            zipf.write(record.audio_file.path, arcname=f'dataset/wavs/{record.file_name}')

    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="dataset.zip"'
    
    return response

@require_POST
def delete_audio_view(request):
    """
    View to 'soft delete' an audio record.
    It only deletes the database entry, leaving the file on disk for later cleanup.
    This avoids Windows file locking issues.
    """
    try:
        data = json.loads(request.body)
        audio_id = data.get('audio_id')
        
        audio_transcription = get_object_or_404(AudioTranscription, pk=audio_id)

        audio_transcription.delete()

        return JsonResponse({'status': 'success', 'message': 'Record deleted from database.'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)