import os
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from src.internal_helpers.json_utils import get_repository_from_json

TRIVY_PATH = os.getenv("TRIVY_PATH", "/opt/homebrew/bin/trivy")

cache_dir = os.path.join(os.getcwd(), '.cache')

def create_cache_dir():
    """Creates a directory for the cache if it does not exist."""
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

def remove_cache_dir():
    """Deletes the cache directory after the work is completed."""
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"Cache directory '{cache_dir}' has been removed.")

def update_trivy_db():
    """Updates the Trivy database before starting a scan."""
    try:
        print("Updating Trivy database...")
        result = subprocess.run(
            [TRIVY_PATH, "image", "--cache-dir", cache_dir, "--download-db-only"],
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

    sleep(5)

def process_json_files_concurrently(json_files):
    """Processes JSON files and builds repositories in parallel."""
    repositories = set()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_repository_from_json, json_file) for json_file in json_files]
        for future in as_completed(futures):
            repositories.update(future.result())
    return list(repositories)

def is_repository_accessible(repository, timeout_duration=60):
    """Checks the availability of the repository using the docker pull command."""
    env = os.environ.copy()
    try:
        result = subprocess.run(
            ["docker","--config","/Users/oksanalevchenko/.docker","pull", repository],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_duration,
            env=env
        )
        if result.returncode != 0:
            print(f"Docker pull failed for {repository}: {result.stderr.decode()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Timeout occurred while pulling {repository}")
        return False

def scan_repository(repository, output_dir, timeout_duration=300):
    """Scans an image using Trivy and saves the results to a JSON file."""
    sanitized_name = repository.replace('/', '-').replace(':', '-')
    output_file = os.path.join(output_dir, f"{sanitized_name}-cve.json")

    if not is_repository_accessible(repository):
        print(f"Skipping repository {repository} as it is not accessible.")
        return

    try:
        env = os.environ.copy()
        result = subprocess.run(
            [TRIVY_PATH, "image", "--platform", "linux/amd64", "-f", "json", "--cache-dir", cache_dir, "-o", output_file, repository],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_duration,
            env=env
        )
        if result.returncode != 0:
            print(f"Trivy failed to scan {repository}: {result.stderr.decode()}")
        elif not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            print(f"Error: No results generated for {repository}.")
    except subprocess.TimeoutExpired:
        print(f"Timeout occurred while inspecting {repository}")

def process_repositories_concurrently(repositories, output_dir):
    """At the same time, it scans repositories with the help of Tribe."""
    create_cache_dir()
    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(scan_repository, repository, output_dir) for repository in repositories]
            for future in futures:
                future.result()
    finally:
        remove_cache_dir()

