#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import csv
import zipfile
import django

# Django loyihangni settings.py ga ulash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CONFIG.settings")
django.setup()

from transcriber.models import AudioTranscription


def export_dataset(output_zip="dataset.zip"):
    """
    Script to generate dataset.zip with metadata.csv and wav files.
    """
    records = AudioTranscription.objects.select_related('speaker').filter(is_checked=True).order_by('created_at')

    string_buffer = io.StringIO()
    csv_writer = csv.writer(string_buffer, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    for record in records:
        transcription = record.transcription_text or ''
        csv_writer.writerow([record.file_name, transcription, record.speaker.code])

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # metadata.csv yozish
        zipf.writestr("dataset/metadata.csv", string_buffer.getvalue().encode("utf-8"))

        # audio fayllarni yozish
        for record in records:
            if record.audio_file and os.path.exists(record.audio_file.path):
                zipf.write(record.audio_file.path, arcname=f"dataset/wavs/{record.file_name}")

    # ZIP faylni saqlash
    with open(output_zip, "wb") as f:
        f.write(zip_buffer.getvalue())

    print(f"✅ Dataset exported to {output_zip}")


if __name__ == "__main__":
    export_dataset()
