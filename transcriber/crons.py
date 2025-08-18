from .models import AudioTranscription
from django.db.models import Q
from google import genai

client = genai.Client(api_key='AIzaSyB0T2_THrBA1mf3pZVwHfGQcRWQ7k0bDn4')

def generate_text_last_audio():  
    try:  
        audio = AudioTranscription.objects.filter(
            Q(transcription_text__isnull=True) | Q(transcription_text="")
        ).first()
        
        myfile = client.files.upload(file=audio.audio_file.path)
        response = client.models.generate_content(
            model="gemini-2.5-pro", contents=["This is a Karakalpak audio. Create a transcription of the speech in the Karakalpak language and the Latin alphabet.", myfile]
        )
        audio.transcription_text = response.text
        audio.save()

    except Exception as e:  
        print(e)
