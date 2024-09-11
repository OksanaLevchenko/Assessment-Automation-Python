import argparse
import os
import json
from datetime import datetime
from notion_client import Client
from src.internal_notion import find_customer, create_assessment_block, create_assessment_page, createAssessmentDB
from src.internal_polaris import importPolarisData
from src.internal_kubescape import importKubescapeData
from src.internal_trivy import importTrivyData
from src.tools import *


def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def main():
    parser = argparse.ArgumentParser(description="Generating Assessment Notion file from combined.json")
    parser.add_argument('-t', '--trivy-combined', type=str, help="Please enter path to the combined.json")
    parser.add_argument('-p', '--polaris', type=str, help="Please enter path to the combined.json")
    parser.add_argument('-k', '--kubescape', type=str, help="Please enter path to the combined.json")
    parser.add_argument('-c', '--customer', type=str, help="Please enter customer name. Ex. 'Qualcomm'", required=True)
    parser.add_argument('-K', '--notion-key', type=str, help="Please enter the value for Notion API Key", required=True)
    args = parser.parse_args()

    if not (args.trivy_combined or args.polaris or args.kubescape):
        parser.error("At least one of --trivy-combined, --polaris, or --kubescape must be provided.")

    auth_token = os.getenv("NOTION_API_KEY") or args.notion_key or input("Please enter the value for Notion API Key: ")

    if not auth_token:
        raise ValueError("Notion API Key is required. Please provide it using the environment variable, command-line argument, or input prompt.")

    notion_session = Client(auth=auth_token)

    trivy_data = load_json_file(args.trivy_combined) if args.trivy_combined else None
    polaris_data = load_json_file(args.polaris) if args.polaris else None
    kubescape_data = load_json_file(args.kubescape) if args.kubescape else None

    custID = find_customer(notion_session, args.customer)
    page = create_assessment_page(notion_session, custID)
    pageID = page['id']

    db = createAssessmentDB(notion_session, pageID)
    dbID = db['id']

    if polaris_data:
        print("Import Polaris data in notion")
        importPolarisData(notion_session, polaris_data, dbID)

    if kubescape_data:
        print("Import Kubescape data in notion")
        importKubescapeData(notion_session, kubescape_data, dbID)

    if trivy_data:
        print("Import Trivy data in notion")
        importTrivyData(notion_session, trivy_data, dbID)


if __name__ == "__main__":
    main()
