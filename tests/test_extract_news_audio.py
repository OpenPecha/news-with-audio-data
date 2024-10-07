import json
from extract_news_audio import has_news_audio

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_has_news_audio():
    # Load news data from a JSON file
    news_data = read_json_file(f'./test_dataset.json')
    expected_results = {
        "1": True,
        "2": False,
        "3": False
    }
    
    for article_id, article in news_data.items():
        expected_result = expected_results[article_id]  # True if audio URL exists, else False
        
        result = has_news_audio(article)
        
        assert result == expected_result, f"Expected {expected_result} but got {result} for article {article_id}"

if __name__ == "__main__":
    test_has_news_audio()
    print("All tests checked!")