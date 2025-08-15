from pydub import AudioSegment, silence
import tempfile
from django.core.files import File

def split_audio(uploaded_file):
    audio = AudioSegment.from_file(uploaded_file, format="mp3")
    file_name = uploaded_file.name.split('.')[0]

    chunks = silence.split_on_silence(
        audio,
        min_silence_len=300,
        silence_thresh=audio.dBFS - 30, 
        keep_silence=300
    )

    for index, chunk in enumerate(chunks, start=1):
        duration_sec = len(chunk) / 1000
        if 5 <= duration_sec <= 25:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            chunk.export(tmp_file.name, format="wav")
            yield File(open(tmp_file.name, "rb"), name=f"{file_name}_{index:04d}.wav")