import pandas as pd

def load_and_clean_data():
    """
    Load and clean the input CSV files by removing whitespace from key fields.

    Returns:
        tuple: A pair of pandas DataFrames:
    """
    # Load the data
    df_speaker_info = pd.read_csv('data/input/gender.csv')
    df_news_data = pd.read_csv('data/output/details/news_data_with_combine_speaker.csv')
    
    # Clean up whitespace in relevant columns
    df_speaker_info['News Channel'] = df_speaker_info['News Channel'].str.strip()
    df_speaker_info['Speaker Name'] = df_speaker_info['Speaker Name'].str.strip()
    df_news_data['Speaker Name'] = df_news_data['Speaker Name'].str.strip()
    
    return df_speaker_info, df_news_data

def create_gender_lookup(df_speaker_info):
    """
    Create a dictionary for efficient gender lookups based on speaker name and news channel.

    Args:
        df_speaker_info (pd.DataFrame): DataFrame containing reference gender information
            Required columns: Speaker Name, News Channel, Speaker Gender

    Returns:
        dict: Dictionary with (speaker_name, news_channel) tuples as keys and gender as values
    """
    return {
        (row['Speaker Name'], row['News Channel']): row['Speaker Gender']
        for _, row in df_speaker_info.iterrows()
    }

def get_gender(row, gender_lookup, missing_genders):
    """
    Process gender information for one or more speakers in a news item.

    Handles multiple speakers separated by commas and tracks missing gender information.

    Args:
        row (pd.Series): A row from the news data DataFrame
            Required fields: Speaker Name, News Channel
        gender_lookup (dict): Dictionary mapping (speaker, channel) to gender
        missing_genders (dict): Dictionary to track speakers with missing gender info

    Returns:
        str: Comma-separated string of gender information for all speakers
    """
    speakers = [name.strip() for name in row['Speaker Name'].split(',')]
    genders = []
    
    for speaker in speakers:
        # Lookup the gender using speaker name and news channel
        gender = gender_lookup.get((speaker, row['News Channel']), '')
        
        if gender:
            genders.append(gender)
        else:
            genders.append(" ")  # Empty gender space if not found
            # Track missing gender information
            if speaker not in missing_genders:
                missing_genders[speaker] = set()
            missing_genders[speaker].add(row['News Channel'])
    
    return ', '.join(genders)

def process_missing_genders(missing_genders):
    """
    Convert the missing genders tracking dictionary to a DataFrame for export.

    Args:
        missing_genders (dict): Dictionary mapping speakers to sets of news channels
            where their gender information is missing

    Returns:
        pd.DataFrame: DataFrame containing speaker names and channels with missing gender info
            Columns: Speaker Name, News Channel
    """
    return pd.DataFrame([
        {'Speaker Name': speaker, 'News Channel': news_channel}
        for speaker, news_channels in missing_genders.items()
        for news_channel in news_channels
    ])

def main():
    # File paths
    filled_gender_csv = 'data/output/details/news_data_with_gender.csv'
    missing_genders_csv = 'data/output/details/missing_genders.csv'
    
    # Load and clean data
    df_speaker_info, df_news_data = load_and_clean_data()
    
    # Create gender lookup dictionary
    gender_lookup = create_gender_lookup(df_speaker_info)
    
    # Dictionary to track speakers without gender
    missing_genders = {}
    
    # Process gender information
    df_news_data['Speaker Gender'] = df_news_data.apply(
        lambda row: get_gender(row, gender_lookup, missing_genders),
        axis=1
    )
    
    # Save processed data
    df_news_data.to_csv(filled_gender_csv, index=False)
    
    # Process and save missing gender information
    missing_genders_df = process_missing_genders(missing_genders)
    missing_genders_df.to_csv(missing_genders_csv, index=False)
    
    # Print completion message
    print(f"CSV file with gender information saved to {filled_gender_csv}")
    print(f"CSV file with missing gender information saved to {missing_genders_csv}")

if __name__ == "__main__":
    main()