import pandas as pd
import re
import os

def create_output_directories(output_paths):
    """Create directories for output files if they don't exist."""
    for path in output_paths:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

def compile_patterns():
    """Compile regex patterns for speaker name extraction.
    Returns:
        dict: A dictionary containing compiled regex patterns

    """
    patterns = {
        'pattern_1': re.compile(
            r'(?:གསར་འགོད་པ།\s*་?\s*)([^\n།]+།|[^\n།]+\n)(?=\s*(?:\n|$))'
        ),
        'pattern_2': re.compile(
            r'(?:གསར་འགོད་པ་།)\s*([^\n།]+།\s*){1,3}(?=\s*(?:\n|$))'
        ),
        'pattern_3': re.compile(
            r'(?:གསར་འགོད་པ།|གསར་འགོད་པ་དང་རྩོམ་སྒྲིག་པ།|གསར་འགོད་པ་དང་རྩོམ་སྒྲིག་པ་།\s*)'
            r'([^\n།]*།(?!\s*\n)\s*(?:(?<!།)དྲྭ་ཐོག་)?[^\n།]*།?)'
        ),
        'pattern_4': re.compile(
            r'གསར་འགོད་པ།\s*([^\n།]+)(?=\s*\n)'
        )
    }
    return patterns

def extract_speaker_names(audio_text, patterns):
    """
    Extract speaker names from the audio text using multiple regex patterns.
    
    Args:
        audio_text (str): The input text to extract speaker names from
        patterns (dict): Dictionary of compiled regex patterns
        
    Returns:
        str or None: Extracted speaker names formatted as a comma-separated string, or None if no names found
    """
    for pattern in patterns.values():
        matches = pattern.findall(audio_text)
        if matches:
            names = []
            for match in matches:
                # Split each match by "།" to get individual names
                individual_names = match.split("།")
                # Clean and add "།" back to each non-empty name
                for name in individual_names:
                    name = name.strip()
                    if name:
                        names.append(f"{name}།")
            
            # Format the processed names as a list-like string
            return ", ".join(names)
    
    return None

def process_audio_data(input_file, output_files):
    """
    Process audio data to extract speaker names and split into separate files.
    
    Args:
        input_file (str): Path to input CSV file
        output_files (dict): Dictionary containing paths for output files
    """
    # Load the CSV file
    df_no_speaker = pd.read_csv(input_file)
    
    # Initialize lists for storing processed data
    with_speaker_data = []
    without_speaker_data = []
    
    # Compile regex patterns
    patterns = compile_patterns()
    
    # Process each row in the DataFrame
    for index, row in df_no_speaker.iterrows():
        audio_text = row['Audio Text']
        speaker_names = extract_speaker_names(audio_text, patterns)
        
        if speaker_names:
            row['Speaker Name'] = speaker_names
            with_speaker_data.append(row)
        else:
            without_speaker_data.append(row)
    
    # Convert lists to DataFrames
    df_with_speaker = pd.DataFrame(with_speaker_data)
    df_without_speaker = pd.DataFrame(without_speaker_data)
    
    # Save the processed data
    df_with_speaker.to_csv(output_files['with_speaker'], index=False, encoding='utf-8')
    df_without_speaker.to_csv(output_files['without_speaker'], index=False, encoding='utf-8')
    
    # Print confirmation messages
    print(f"CSV file with speaker names saved to {output_files['with_speaker']}")
    print(f"CSV file without speaker names saved to {output_files['without_speaker']}")

def main():
    # Define file paths
    file_paths = {
        'input': 'data/news_audio_with_duration - news_audio_with_duration.csv',
        'output': {
            'with_speaker': 'data/output/details/news_data_with_combine_speaker.csv',
            'without_speaker': 'data/output/details/news_data_without_combine_speaker.csv'
        }
    }
    
    # Create output directories
    create_output_directories(file_paths['output'].values())
    
    # Process the audio data
    process_audio_data(file_paths['input'], file_paths['output'])

if __name__ == "__main__":
    main()