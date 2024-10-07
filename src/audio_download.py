import os
import requests

def download_rfa_audio(df, output_dir, session):
    """Downloads RFA audio files based on the provided DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing audio metadata.
        output_dir (str): Directory where audio files will be saved.
        session (requests.Session): Session object for making requests.
    """
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
        "cache-control": "max-age=0",
        "cookie": "AMCVS_518ABC7455E462B97F000101%40AdobeOrg=1; s_cc=true; utag_main=v_id:019169eade56002296e6ea4a443c0507d001b075008f7$_sn:11$_se:5$_ss:0$_st:1727788387180$vapi_domain:rfa.org$ses_id:1727793787%3Bexp-session$_pn:5%3Bexp-session; AMCV_518ABC7455E462B97F000101%40AdobeOrg=1176715910%7CMCIDTS%7C19997%7CMCMID%7C92058839809215745258174654077801968713%7CMCAID%7CNONE%7CMCOPTOUT-1727793787s%7CNONE%7CvVersion%7C5.4.0; s_sq=%5B%5BB%5D%5D",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }

    os.makedirs(output_dir, exist_ok=True)

    for index, row in df.iterrows():
        audio_url = row['Audio URL']
        audio_id = row['ID']
        news_channel = row['News Channel']

        if news_channel == 'RFA':
            try:
                if audio_url and audio_url != 'URL not found':
                    # Define the audio file path
                    audio_file_path = os.path.join(output_dir, f'{audio_id}.mp3')
                    
                    # Check if the audio file already exists
                    if not os.path.exists(audio_file_path):
                        response = session.get(audio_url, headers=headers, stream=True)
                        response.raise_for_status()  # Check for HTTP errors

                        # Save the audio file
                        with open(audio_file_path, 'wb') as audio_file:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:
                                    audio_file.write(chunk)

                        print(f"Downloaded RFA audio: {audio_id}.mp3")
                    else:
                        print(f"Audio file {audio_id}.mp3 already exists. Skipping download.")
                else:
                    print(f"No valid audio URL found for RFA ID: {audio_id}")
            except Exception as e:
                print(f"Failed to access or download RFA URL {audio_url}: {e}")
