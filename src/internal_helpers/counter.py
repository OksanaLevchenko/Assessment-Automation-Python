import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

def search_words_in_json(json_file, words_to_search):
    """Шукає слова в JSON-файлі."""
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    json_string = json.dumps(data)
    word_count = Counter()

    for word in words_to_search:
        word_count[word] = json_string.lower().count(word.lower())

    return word_count

def count_cves(combined_json):
    """Підраховує CVEs у JSON-файлі."""
    words_to_search = ['HIGH', 'CRITICAL', 'MEDIUM', 'LOW', 'UNKNOWN']
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(search_words_in_json, combined_json, words_to_search)
        result = future.result()

    for word, count in result.items():
        print(f"{word}: {count}")
