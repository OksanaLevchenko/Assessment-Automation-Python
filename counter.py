import json
import argparse
from collections import Counter


def search_words_in_json(json_file, words_to_search):

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    json_string = json.dumps(data)

    word_count = Counter()

    for word in words_to_search:
        count = json_string.lower().count(word.lower())
        word_count[word] = count

    return word_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prints the number of CVIs from combined.json")
    parser.add_argument('-f','--file',type=str,help="Please enter path to the combined.json",required=True)
    args = parser.parse_args()

    json_file = args.file
    words_to_search = ['HIGH', 'CRITICAL', 'MEDIUM', 'LOW', 'UNKNOWN']

    result = search_words_in_json(json_file, words_to_search)
    
    for word, count in result.items():
        print(f"{word}: {count}")
