import os
import zipfile

audio_dir = "media/wavs"
zip_file = "all_audios.zip"

def zip_audios(audio_dir, zip_file):
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(audio_dir):
            for file in files:
                if file.lower().endswith(('.wav')):
                    file_path = os.path.join(root, file)
                    # papka ichidagi nisbiy yo‘lini qo‘shamiz
                    arcname = os.path.relpath(file_path, audio_dir)
                    zipf.write(file_path, arcname)
                    print(f"Qo‘shildi: {arcname}")
    print(f"\nBarcha audio fayllar '{zip_file}' ichiga yig‘ildi.")

if __name__ == "__main__":
    zip_audios(audio_dir, zip_file)
