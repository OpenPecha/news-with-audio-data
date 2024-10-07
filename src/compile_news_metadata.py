import os
import pandas as pd
import requests
import re
import json

data_root_dir = './data'  
news_channels = ['RFA', 'VOA', 'VOT']

data_list = []

# Regex pattern for validating URLs
url_pattern = re.compile(r'^(http|https)://.*$')

# Headers for RFA requests
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

def extract_speaker_from_text(body_text_lines):
    """Extracts the speaker's name (the word immediately following 'གསར་འགོད་པ།') from the text.

    Args:
        body_text_lines (list): List of lines in the text.

    Returns:
        str: Extracted speaker's name or an empty string if not found.
    """
    full_text = ' '.join(body_text_lines).replace('\n', ' ').strip()
    print(f"Full text for speaker extraction: {full_text}")  
    match = re.search(r'གསར་འགོད་པ།\s*(\S+)', full_text)
    
    if match:
        print(f"Extracted speaker name: {match.group(1)}") 
        return match.group(1)  # Return the word after 'གསར་འགོད་པ།'
    
    return ''  # Return empty if no match is found


for channel in news_channels:
    channel_dir = os.path.join(data_root_dir, channel, 'news_dataset_with_audio')
    
    if not os.path.exists(channel_dir):
        print(f"Directory {channel_dir} not found.")
        continue
    
    for root, dirs, files in os.walk(channel_dir):
        audio_id = os.path.basename(root)  # Get the folder name as the ID
        audio_url = None
        audio_text = ''  
        speaker_name = ''
        speaker_gender = ''
        publishing_year = ''
        author = ''
        
        for file in files:
            if file.endswith('.txt') and file != 'news_text.txt':
                audio_url_path = os.path.join(root, file)
                with open(audio_url_path, 'r', encoding='utf-8') as f:
                    url_content = f.read().strip()  # Read the URL and strip whitespace
                    if url_pattern.match(url_content):  # Validate if it's a URL
                        audio_url = url_content
            
            if file == 'news_text.txt':
                text_file_path = os.path.join(root, file)
                if os.path.exists(text_file_path):
                    with open(text_file_path, 'r', encoding='utf-8') as f:
                        audio_text_lines = f.readlines()  # Read all lines as a list
                        audio_text = ''.join(audio_text_lines).strip()  # Join all lines into a single string
                        
                        # Extract speaker name from text for RFA and VOT if not already found in metadata
                        if channel == 'RFA': 
                            speaker_name = extract_speaker_from_text(audio_text_lines)

            # Check for metadata JSON files
            if file.endswith('.json'):
                metadata_path = os.path.join(root, file)
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                        if channel == 'VOA':
                            # Correct the publishing year for VOA
                            publishing_year = metadata.get('author', '') 
                            speaker_name = metadata.get('speaker', '') 
                        else:
                            # Use regular metadata for RFA and VOT
                            speaker_name_metadata = metadata.get('speaker', '')
                            # Only use speaker name from metadata if it is not 'unknown'
                            if speaker_name_metadata.lower() != 'unknown' and not speaker_name:
                                speaker_name = speaker_name_metadata
                            publishing_year = metadata.get('published_date', '') 
                            speaker_gender = metadata.get('gender', '')

        data_list.append({
            'ID': audio_id,
            'Audio URL': audio_url if audio_url else 'URL not found',
            'Audio Text': audio_text if audio_text else 'Transcript not found',
            'Speaker Name': speaker_name,
            'Speaker Gender': speaker_gender,
            'News Channel': channel,  
            'Publishing Year': publishing_year
        })

# Sort data_list by ID
data_list.sort(key=lambda x: x['ID'])

# Create DataFrame and save to CSV
df = pd.DataFrame(data_list, columns=['ID', 'Audio URL', 'Audio Text', 'Speaker Name', 'Speaker Gender', 'News Channel', 'Publishing Year'])
output_metadata_csv_path = './news_data.csv'
df.to_csv(output_metadata_csv_path, index=False, encoding='utf-8')
print(f"CSV file saved at {output_metadata_csv_path}")

# Create a session object
session = requests.Session()
session.headers.update(headers)

# Directory to save downloaded RFA audio
rfa_audio_dir = os.path.join(data_root_dir, 'RFA', 'downloaded_audio')
os.makedirs(rfa_audio_dir, exist_ok=True)
