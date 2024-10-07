import os
import pandas as pd
from mutagen.mp3 import MP3  # To get audio duration
from datetime import datetime


metadata_csv_path = './news_audio_with_duration.csv'
df = pd.read_csv(metadata_csv_path)

updated_data = []

for index, row in df.iterrows():
    audio_id = row['ID']
    audio_url = row['Audio URL']
    audio_text = row['Audio Text']
    speaker_name = row['Speaker Name']
    speaker_gender = row['Speaker Gender']
    news_channel = row['News Channel']
    publishing_year = row['Publishing Year']
    
    audio_duration = 'Duration not found'

    audio_file_path = os.path.join('./data', news_channel, 'downloaded_audio', f"{audio_id}.mp3")

    if os.path.exists(audio_file_path):
        try:
            audio = MP3(audio_file_path)
            audio_duration = str(datetime.utcfromtimestamp(audio.info.length).strftime('%H:%M:%S'))
        except Exception as e:
            print(f"Error reading duration for {audio_file_path}: {e}")

    updated_data.append({
        'ID': audio_id,
        'Audio URL': audio_url,
        'Audio Text': audio_text,
        'Audio Duration': audio_duration,
        'Speaker Name': speaker_name,
        'Speaker Gender': speaker_gender,
        'News Channel': news_channel,
        'Publishing Year': publishing_year
    })

updated_df = pd.DataFrame(updated_data)

output_updated_csv_path = './news_data_with_duration.csv'
updated_df.to_csv(output_updated_csv_path, index=False, encoding='utf-8')

print(f"Updated CSV file saved at {output_updated_csv_path}")
