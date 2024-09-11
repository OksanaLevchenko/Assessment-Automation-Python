import os
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from src.internal_helpers.json_utils import get_repository_from_json

# Створюємо кеш в папці проекту
cache_dir = os.path.join(os.getcwd(), '.cache')

def create_cache_dir():
    """Створює директорію для кешу, якщо вона не існує."""
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

def remove_cache_dir():
    """Видаляє директорію кешу після завершення роботи."""
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"Cache directory '{cache_dir}' has been removed.")

def update_trivy_db():
    """Оновлює базу даних Trivy перед запуском сканування."""
    try:
        print("Updating Trivy database...")
        result = subprocess.run(
            ["trivy", "image",  "--platform", "linux/amd64", "--cache-dir", cache_dir, "--download-db-only"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print("Trivy database updated successfully.")
        else:
            print(f"Failed to update Trivy database: {result.stderr.decode()}")
            sys.exit(1)
    except subprocess.SubprocessError as e:
        print(f"Error while updating Trivy database: {str(e)}")
        sys.exit(1)

    # Додаємо невелику затримку після оновлення бази даних, щоб переконатися, що все завершено
    sleep(5)

def process_json_files_concurrently(json_files):
    """Паралельно обробляє JSON-файли та збирає репозиторії."""
    repositories = set()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_repository_from_json, json_file) for json_file in json_files]
        for future in as_completed(futures):
            repositories.update(future.result())
    return list(repositories)

def is_repository_accessible(repository, timeout_duration=60):
    """Перевіряє доступність репозиторію за допомогою команди docker pull."""
    try:
        result = subprocess.run(
            ["docker", "pull" ,"--platform", "linux/amd64", repository],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_duration
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Timeout occurred while pulling {repository}")
        return False

def scan_repository(repository, output_dir, timeout_duration=300):
    """Сканує образ за допомогою Trivy і зберігає результати у JSON-файлі."""
    sanitized_name = repository.replace('/', '-').replace(':', '-')
    output_file = os.path.join(output_dir, f"{sanitized_name}-cve.json")

    if not is_repository_accessible(repository):
        print(f"Skipping repository {repository} as it is not accessible.")
        return

    try:
        result = subprocess.run(
            ["trivy", "image", "--platform", "linux/amd64", "-f", "json", "--cache-dir", cache_dir, "-o", output_file, repository],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_duration
        )
        if result.returncode != 0:
            print(f"Trivy failed to scan {repository}: {result.stderr.decode()}")
        elif not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            print(f"Error: No results generated for {repository}.")
    except subprocess.TimeoutExpired:
        print(f"Timeout occurred while inspecting {repository}")

def process_repositories_concurrently(repositories, output_dir):
    """Паралельно сканує репозиторії за допомогою Trivy."""
    create_cache_dir()
    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(scan_repository, repository, output_dir) for repository in repositories]
            for future in futures:
                future.result()
    finally:
        remove_cache_dir()

