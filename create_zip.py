import pandas as pd
import zipfile
import os

csv_file = "for_zip.csv"
df = pd.read_csv(csv_file)

audio_dir = "media/wavs"

zip_filename = "audio_files.zip"

with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for filename in df["Fayl nomi"]:
        filepath = os.path.join(audio_dir, filename)
        if os.path.exists(filepath):
            zipf.write(filepath, arcname=filename)
        else:
            print(f"⚠️ Fayl topilmadi: {filepath}")

print(f"✅ Barcha fayllar '{zip_filename}' ichiga yig‘ildi!")
