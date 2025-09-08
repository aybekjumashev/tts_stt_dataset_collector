# !pip install librosa matplotlib numpy pandas soundfile

import os
import librosa
import numpy as np
import pandas as pd
import warnings

# Suppress runtime warnings from librosa
warnings.filterwarnings("ignore", category=UserWarning)

# 1. The folder containing all the audio files you want to classify.
FOLDER_TO_CLASSIFY = 'media/wavs/'

# 2. The filename of your reference CLEAN audio file.
#    (This file MUST be inside the folder defined above).
CLEAN_REFERENCE_FILE = 'internatta2_0008.wav' 

# 3. The filename of your reference POOR QUALITY audio file.
#    (This file MUST also be inside the folder defined above).
POOR_QUALITY_REFERENCE_FILE = 'audio1.wav'


def calculate_clarity_score(audio_path):
    """
    Calculates a 'Clarity Score' based on the standard deviation of spectral contrast.
    Based on data analysis, a LOWER score indicates cleaner audio for this specific dataset.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None)
        if len(y) < sr * 0.5: return 10.0 # Default for very short files
        S = np.abs(librosa.stft(y))
        contrast = librosa.feature.spectral_contrast(S=S, sr=sr)
        clarity_score = np.mean(np.std(contrast, axis=1))
        return clarity_score
    except Exception as e:
        print(f"  Error processing {os.path.basename(audio_path)}: {e}")
        return 999.0 # Return a high error score

print("--- Determining Quality Threshold from Your Sample Files ---")

clean_audio_path = os.path.join('media/test/', CLEAN_REFERENCE_FILE)
poor_quality_audio_path = os.path.join('media/test/', POOR_QUALITY_REFERENCE_FILE)

clean_score = calculate_clarity_score(clean_audio_path)
poor_score = calculate_clarity_score(poor_quality_audio_path)

print(clean_score, poor_score)

if clean_score < 999.0 and poor_score < 999.0: # Check for processing errors
    print(f"Clarity Score for Clean Audio ('{CLEAN_REFERENCE_FILE}'): {clean_score:.2f}")
    print(f"Clarity Score for Poor Quality Audio ('{POOR_QUALITY_REFERENCE_FILE}'): {poor_score:.2f}")

    QUALITY_THRESHOLD = (clean_score + poor_score) / 2
    print(f"\n==> ADAPTED QUALITY THRESHOLD SET TO: {QUALITY_THRESHOLD:.2f} <==")
    # --- UPDATED LOGIC DESCRIPTION ---
    print("(Files with a score < threshold will be marked as Clean)")

    classification_results = []
    valid_extensions = ('.wav', '.mp3', '.flac', '.m4a')

    print(f"\n--- Starting Quality Classification for files in '{FOLDER_TO_CLASSIFY}' ---")

    for filename in sorted(os.listdir(FOLDER_TO_CLASSIFY)):
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(FOLDER_TO_CLASSIFY, filename)
            
            score = calculate_clarity_score(file_path)
            
            # --- THE CRITICAL FIX: The logic is now INVERTED ---
            # If the score is LOWER than the threshold, it is CLEAN.
            if score < QUALITY_THRESHOLD:
                classification = 0 # Clean
                result_text = "Clean"
            else:
                classification = 1 # Poor Quality
                result_text = "Poor Quality"
            
            classification_results.append({
                'Filename': filename,
                'Classification': classification,
                'Clarity Score': f"{score:.2f}",
                'Result': result_text
            })

    if classification_results:
        results_df = pd.DataFrame(classification_results)
        print("\n--- AUDIO QUALITY REPORT ---")
        print(results_df.to_string(index=False))

        output_file = "audio_tone_analysis_results.csv"
        results_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n✅ Natijalar '{output_file}' fayliga saqlandi.")
    else:
        print(f"\nNo valid audio files were found in the '{FOLDER_TO_CLASSIFY}' folder.")

else:
    print("\n--- SCRIPT HALTED ---")
    print("Could not calculate scores for the reference audio files.")
    print("Please check that the filenames and folder name in the 'CONFIGURATION' section are correct.")