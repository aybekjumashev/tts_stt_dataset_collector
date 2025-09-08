import librosa
import numpy as np
import os
import glob
# from tqdm.notebook import tqdm
import pandas as pd

INPUT_DIR = 'media/wavs/'


# 1. Amplituda Chegaralari
AMPLITUDE_SILENCE_THRESHOLD = 0.015 # Biroz ko'tarildi, fon shovqiniga ruxsat berish uchun
AMPLITUDE_NOISE_THRESHOLD = 0.1     # O'zgarishsiz, bu chegara yaxshi ishlayapti

# 2. Tahlil Oynasi (Frame) Sozlamalari
FRAME_DURATION_MS = 20 # Qisqartirildi, nozik shovqinlarni "ushlash" uchun

# 3. Kontekstni Tekshirish Sozlamalari
CONTEXT_WINDOW_FRAMES = 5 # O'zgarishsiz

# --- Umumiy Sozlamalar ---
TRIM_THRESHOLD_DB = 20

def analyze_tail_with_heuristic(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        _, index = librosa.effects.trim(y, top_db=TRIM_THRESHOLD_DB)
        tail_segment = y[index[1]:]

        frame_length = int(sr * FRAME_DURATION_MS / 1000)
        if len(tail_segment) < frame_length * (CONTEXT_WINDOW_FRAMES + 1):
            return 0

        frames = librosa.util.frame(tail_segment, frame_length=frame_length, hop_length=frame_length)
        
        for i in range(CONTEXT_WINDOW_FRAMES, frames.shape[1]):
            current_frame = frames[:, i]
            context_frames = frames[:, i - CONTEXT_WINDOW_FRAMES : i]
            
            max_amp_current = np.max(np.abs(current_frame))
            is_current_suspicious = (AMPLITUDE_SILENCE_THRESHOLD < max_amp_current < AMPLITUDE_NOISE_THRESHOLD)
            
            if is_current_suspicious:
                max_amp_context = np.max(np.abs(context_frames))
                is_context_silent = max_amp_context < AMPLITUDE_SILENCE_THRESHOLD
                
                if is_context_silent:
                    return 1 # "Iflos" deb topildi
        return 0 # "Toza" deb topildi
        
    except Exception as e:
        print(f"\n'{os.path.basename(audio_path)}' faylini tahlil qilishda xato: {e}")
        return -1

audio_files = glob.glob(os.path.join(INPUT_DIR, '*.wav'))
if not audio_files:
    print(f"Xatolik: '{INPUT_DIR}' papkasida .wav fayllar topilmadi.")
else:
    print(f"Jami {len(audio_files)} ta fayl topildi. Yangi parametrlar bilan tahlil boshlandi...")
    
    all_results = []
    
    for audio_path in audio_files:
        is_noisy_flag = analyze_tail_with_heuristic(audio_path)
        
        if is_noisy_flag != -1:
            all_results.append({
                'file_name': os.path.basename(audio_path),
                'is_noisy': is_noisy_flag
            })

    if all_results:
        df = pd.DataFrame(all_results)
        df = df.sort_values(by='is_noisy', ascending=False).reset_index(drop=True)

        print(f"\n\n--- Audio Fayllarning Tozaligi Bo'yicha Yangilangan Hevristik Tahlil ---")
        print(df.to_string())
        df.to_csv("audio_analysis_results.csv", index=False, encoding="utf-8-sig")
        
        noisy_count = df['is_noisy'].sum()
        clean_count = len(df) - noisy_count
        print(f"\nXulosa: {noisy_count} ta faylda nafas/shovqin aniqlandi, {clean_count} ta fayl toza deb topildi.")