# transcriber/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import AudioTranscription, Speaker
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
import json
import io
import zipfile
import csv 
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .utils import split_audio
import datetime



@login_required
def main_view(request):
    """
    Display the main page with filtering, search, pagination, and statistics.
    """
    total_audios = AudioTranscription.objects.count()
    with_transcription_count = AudioTranscription.objects.filter(is_checked=True).count()
    without_transcription_count = total_audios - with_transcription_count

    total_time = 0
    for audio in AudioTranscription.objects.all():
        total_time += audio.duration_seconds
    
    with_transcription_time = 0
    for audio in AudioTranscription.objects.filter(is_checked=True):
        with_transcription_time += audio.duration_seconds

    without_transcription_time = total_time - with_transcription_time



    queryset = AudioTranscription.objects.all().order_by('-created_at')
    speakers = Speaker.objects.all()

    filter_by = request.GET.get('filter_by', 'all')
    if filter_by == 'with_transcription_all':
        queryset = queryset.exclude(Q(transcription_text__isnull=True) | Q(transcription_text__exact=''))
    elif filter_by == 'with_transcription_checked':
        queryset = queryset.filter(is_checked=True)
    elif filter_by == 'with_transcription_not_checked':
        queryset = queryset.exclude(Q(transcription_text__isnull=True) | Q(transcription_text__exact=''))
        queryset = queryset.filter(is_checked=False)
    elif filter_by == 'without_transcription':
        queryset = queryset.filter(Q(transcription_text__isnull=True) | Q(transcription_text__exact=''))
    
    
    speaker_filter = request.GET.get('speaker', 'all')
    if speaker_filter != 'all' and speaker_filter.isdigit():
        queryset = queryset.filter(speaker__id=speaker_filter)

    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            Q(transcription_text__icontains=search_query) |
            Q(audio_file__icontains=search_query) |
            Q(speaker__name__icontains=search_query) |
            Q(speaker__code__icontains=search_query)
        )

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'speakers': speakers,
        'filter_by': filter_by,
        'speaker_filter': speaker_filter,
        'q': search_query,
        'result_audios': queryset.count(),
        'stats': {
            'total': total_audios,
            'total_time': datetime.timedelta(seconds=total_time),
            'with_transcription': with_transcription_count,
            'with_transcription_time': datetime.timedelta(seconds=with_transcription_time),
            'without_transcription': without_transcription_count,
            'without_transcription_time': datetime.timedelta(seconds=without_transcription_time),
        }
    }
    return render(request, 'index.html', context)



@require_POST
def upload_audio_view(request):
    uploaded_files = request.FILES.getlist('audio_files')
    speaker_id = request.POST.get('speaker')
    if not speaker_id:
        return redirect('main_view')

    speaker = get_object_or_404(Speaker, pk=speaker_id)

    for file in uploaded_files:
        for chunk_file in split_audio(file):
            AudioTranscription.objects.create(audio_file=chunk_file, speaker=speaker)

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
    records = AudioTranscription.objects.select_related('speaker').filter(is_checked=True).order_by('created_at')
    string_buffer = io.StringIO()
    
    csv_writer = csv.writer(string_buffer, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    for record in records:
        transcription = record.transcription_text or ''
        csv_writer.writerow([record.file_name, transcription, record.speaker.code])

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


@require_POST
def finish_audio_view(request):
    """
    Marks a specific audio transcription as checked/finished.
    """
    try:
        data = json.loads(request.body)
        audio_id = data.get('audio_id')
        transcription = data.get('transcription')
        
        audio_transcription = get_object_or_404(AudioTranscription, pk=audio_id)
        audio_transcription.is_checked = True
        audio_transcription.transcription_text = transcription
        audio_transcription.save()

        return JsonResponse({'status': 'success', 'message': 'Audio marked as finished.'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)