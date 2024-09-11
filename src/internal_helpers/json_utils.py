import os
import json
from concurrent.futures import ThreadPoolExecutor

def load_json_file(file_path):
    """Завантажує JSON-файл і повертає його вміст."""
    with open(file_path, 'r') as file:
        return json.load(file)

def find_json_files(path):
    """Знаходить всі JSON файли в зазначеній директорії."""
    json_files = []
    for root, dirs, files in os.walk(path):
        json_files.extend([os.path.join(root, file) for file in files if file.endswith(".json")])
    return json_files

def search_keys_in_json(data):
    """Шукає всі зображення в полі 'image' та додає їх у список репозиторіїв."""
    repositories = set()

    if isinstance(data, dict):
        image = data.get('image')
        if isinstance(image, str):
            repositories.add(image)
        elif isinstance(image, dict):
            repository = image.get('repository')
            tag = image.get('tag', '')
            if repository:
                full_repository = f"{repository}:{tag}" if tag else repository
                repositories.add(full_repository)

        for value in data.values():
            repositories.update(search_keys_in_json(value))

    elif isinstance(data, list):
        for item in data:
            repositories.update(search_keys_in_json(item))

    return repositories

def get_repository_from_json(json_file):
    """Знаходить репозиторії у JSON-файлах."""
    repositories = set()
    if os.path.getsize(json_file) == 0:
        return repositories

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            repositories.update(search_keys_in_json(data))
    except json.JSONDecodeError as e:
        print(f"Warning: Could not decode {json_file}: {e}")
    return repositories

def merge_json_files(output_dir):
    """Паралельно об'єднує всі результати у один JSON-файл."""
    combined_data = []
    
    def process_file(file):
        if file.endswith("-cve.json"):
            with open(os.path.join(output_dir, file), 'r') as f:
                try:
                    data = json.load(f)
                    return data
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode {file}. Skipping.")
        return None

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, file) for file in os.listdir(output_dir)]
        for future in futures:
            result = future.result()
            if result:
                combined_data.append(result)

    combined_file = os.path.join(output_dir, "combined.json")
    with open(combined_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

    return combined_file
