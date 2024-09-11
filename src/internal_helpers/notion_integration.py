from notion_client import Client
from src.internal_helpers.json_utils import load_json_file
from src.internal_notion import find_customer, create_assessment_page, createAssessmentDB
from src.internal_polaris import importPolarisData
from src.internal_kubescape import importKubescapeData
from src.internal_trivy import importTrivyData

def run_python_scripts(combined_json, polaris_file, kubescape_file, customer_name, notion_key):
    """Імпортує дані в Notion."""
    trivy_data = load_json_file(combined_json) if combined_json else None
    polaris_data = load_json_file(polaris_file) if polaris_file else None
    kubescape_data = load_json_file(kubescape_file) if kubescape_file else None

    notion_session = Client(auth=notion_key)

    custID = find_customer(notion_session, customer_name)
    page = create_assessment_page(notion_session, custID)
    pageID = page['id']
    db = createAssessmentDB(notion_session, pageID)
    dbID = db['id']

    if polaris_data:
        importPolarisData(notion_session, polaris_data, dbID)
    if kubescape_data:
        importKubescapeData(notion_session, kubescape_data, dbID)
    if trivy_data:
        importTrivyData(notion_session, trivy_data, dbID)
