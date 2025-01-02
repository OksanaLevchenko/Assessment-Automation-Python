import os
import json
from concurrent.futures import ThreadPoolExecutor

TARGET_VERSION = "v1.28.12"  # Версія для перевірки

def load_json_file(file_path):
    """Loads a JSON file and returns its contents."""
    with open(file_path, 'r') as file:
        return json.load(file)

def find_json_files(path):
    """Finds all JSON files in the specified directory."""
    json_files = []
    for root, dirs, files in os.walk(path):
        json_files.extend([os.path.join(root, file) for file in files if file.endswith(".json")])
    return json_files

def check_image_version(image):
    """Checks if the image tag matches the TARGET_VERSION."""
    if isinstance(image, str) and ":" in image:
        repo, tag = image.rsplit(":", 1)
        return tag == TARGET_VERSION
    return False

def search_keys_in_json(data):
    """Searches for an image with a specific version in the 'image' field."""
    matching_repositories = set()

    if isinstance(data, dict):
        image = data.get('image')
        if isinstance(image, str) and check_image_version(image):
            matching_repositories.add(image)
        elif isinstance(image, dict):
            repository = image.get('repository')
            tag = image.get('tag', '')
            if repository and tag == TARGET_VERSION:
                full_repository = f"{repository}:{tag}"
                matching_repositories.add(full_repository)

        for value in data.values():
            matching_repositories.update(search_keys_in_json(value))

    elif isinstance(data, list):
        for item in data:
            matching_repositories.update(search_keys_in_json(item))

    return matching_repositories

def get_repository_from_json(json_file):
    """Finds repositories in JSON files."""
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
    """Combines all results into a single JSON file in parallel."""
    combined_data = []
    
    def process_file(file):
        if file.endswith(".json"):
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