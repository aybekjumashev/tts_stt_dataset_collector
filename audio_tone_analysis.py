# !pip install librosa numpy pandas soundfile

import os
import librosa
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

FOLDER_TO_CLASSIFY = 'media/wavs/'


AUDIO_CLASSES = {
    "internatta": {
        "threshold": 4.95
    },
    "jamiyla": {
        "threshold": 4.92
    },
    "jat_jurttagi_jeti_kun": {
        "threshold": 5.48
    },
    "kishkene_shahzada": {
        "threshold": 6.23
    },
    "tumaris": {
        "threshold": 5.99
    }
}

def calculate_clarity_score(audio_path):
    """
    Audioning spektral kontrastining standart og'ishi asosida 'Aniqlik Ko'rsatkichi'ni hisoblaydi.
    Bizning tahlillarimizga ko'ra, bu ko'rsatkich qancha past bo'lsa, audio shuncha toza.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None)
        if len(y) < sr * 0.5: return 10.0
        
        S = np.abs(librosa.stft(y))
        contrast = librosa.feature.spectral_contrast(S=S, sr=sr)
        clarity_score = np.mean(np.std(contrast, axis=1))
        return clarity_score
    except Exception as e:
        print(f"  Xatolik ({os.path.basename(audio_path)}): {e}")
        return 999.0

classification_results = []
valid_extensions = ('.wav', '.mp3', '.flac', '.m4a')

print(f"--- '{FOLDER_TO_CLASSIFY}' papkasidagi fayllarni tasniflash boshlandi ---")
print("Har bir fayl o'z klassiga tegishli shaxsiy chegara bilan solishtiriladi.")

for filename in sorted(os.listdir(FOLDER_TO_CLASSIFY)):
    if filename.lower().endswith(valid_extensions):
        file_path = os.path.join(FOLDER_TO_CLASSIFY, filename)
        
        file_class = None
        quality_threshold = None
        for class_name in AUDIO_CLASSES:
            if class_name in filename.lower():
                file_class = class_name
                quality_threshold = AUDIO_CLASSES[class_name]['threshold']
                break
        
        if file_class:
            score = calculate_clarity_score(file_path)
            
            if score < quality_threshold:
                classification = 0 # Toza
                result_text = "Toza"
            else:
                classification = 1 # Sifatsiz
                result_text = "Sifatsiz"
            
            classification_results.append({
                'Fayl nomi': filename,
                'Tasnifi': classification,
                'Aniqlik Ko\'rsatkichi': f"{score:.2f}",
                'Natija': result_text
            })
        else:
            print(f"  Ogohlantirish: '{filename}' fayli uchun klass topilmadi. O'tkazib yuborildi.")

if classification_results:
    results_df = pd.DataFrame(classification_results)
    # print("\n--- AUDIO SIFATI BO'YICHA YAKUNIY HISOBOT ---")
    # print(results_df.to_string(index=False))
    results_df.to_csv("audio_tone_analysis_results.csv", index=False, encoding="utf-8-sig")
else:
    print(f"\n'{FOLDER_TO_CLASSIFY}' papkasida tasniflanadigan audio fayllar topilmadi.")