import os
import sys
import time
import argparse
from src.internal_helpers.json_utils import find_json_files, merge_json_files
from src.internal_helpers.trivy_processor import process_json_files_concurrently, process_repositories_concurrently, update_trivy_db
from src.internal_helpers.notion_integration import run_python_scripts
from src.internal_helpers.counter import count_cves

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process JSON files and generate assessment.")
    parser.add_argument('-t', '--trivy', required=True, help="Path to the directory where JSON files are located (mandatory).")
    parser.add_argument('-p', '--polaris', help="Path to the Polaris file (optional).")
    parser.add_argument('-k', '--kubescape', help="Path to the Kubescape file (optional).")
    parser.add_argument('-c', '--customer', required=True, help="Customer name to be used in the assessment (mandatory).")
    parser.add_argument('-K', '--notion_key', required=True, help="Notion API key for accessing Notion databases (mandatory).")
    return parser.parse_args()

def main():
    update_trivy_db()
    args = parse_arguments()

    if not os.path.exists(args.trivy):
        print("Error: The path specified for Trivy files does not exist.")
        sys.exit(1)

    output_dir = f"data/script_outputs/{args.customer}"
    os.makedirs(output_dir, exist_ok=True)

    json_files = find_json_files(args.trivy)
    if not json_files:
        print("No JSON files found in the specified directory.")
        sys.exit(1)

    repositories = process_json_files_concurrently(json_files)
    if not repositories:
        print("No repositories found in the JSON files.")
        sys.exit(1)

    process_repositories_concurrently(repositories, output_dir)

    combined_json = merge_json_files(output_dir)

    if os.path.exists(combined_json):
        print(f"Combined JSON file {combined_json} successfully created.")
        count_cves(combined_json)
    else:
        print(f"Error: Combined JSON file {combined_json} was not created.")
        sys.exit(1)

    run_python_scripts(combined_json, args.polaris, args.kubescape, args.customer, args.notion_key)

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Script executed in {end_time - start_time:.2f} seconds")
