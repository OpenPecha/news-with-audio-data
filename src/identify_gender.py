import librosa
import numpy as np

def classify_gender(audio_file):
    # Load the audio file (mp3 supported by librosa)
    y, sr = librosa.load(audio_file, sr=None)  # sr=None to preserve the original sample rate
    
    # Extract the pitch (F0) from the audio
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    
    # Extract the fundamental frequencies (F0)
    pitch_values = []
    for t in range(pitches.shape[1]):
        pitch = pitches[:, t]
        mag = magnitudes[:, t]
        index = mag.argmax()
        pitch_value = pitch[index]
        if pitch_value > 0:
            pitch_values.append(pitch_value)
    
    # Calculate the average pitch
    if len(pitch_values) == 0:
        return "Unable to classify"
    
    avg_pitch = np.mean(pitch_values)
    
    # Set a threshold for male and female (general threshold around 165 Hz)
    if avg_pitch > 165:  # Female
        return "Female"
    else:  # Male
        return "Male"

# Example usage
audio_file = "./T082024DK-2.mp3"
gender = classify_gender(audio_file)
print(f'The speaker is classified as: {gender}')