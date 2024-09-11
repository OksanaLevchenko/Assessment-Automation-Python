import time
from notion_client.errors import HTTPResponseError

def InsertToAssessmentDB(notion_session, dbID, name, namespace, kind, rule, violationType, severity, message, source):
    parentDict = {"database_id": dbID}
    propertiesDict = {
        "Resource Name": {"title": [{"text": {"content": name}}]},
        "Namespace": {"rich_text": [{"text": {"content": namespace}}]},
        "Resource Type": {"rich_text": [{"text": {"content": kind}}]},
        "Rule Violated": {"rich_text": [{"text": {"content": rule}}]},
        "Violation Type": {"rich_text": [{"text": {"content": violationType}}]},
        "Violation Severity": {"multi_select": [{"name": severity}]},
        "Violation Message": {"rich_text": [{"text": {"content": message}}]},
        "Data Source": {"multi_select": [{"name": source}]},
    }

    retries = 5 
    delay = 2 

    for attempt in range(retries):
        try:
            return notion_session.pages.create(parent=parentDict, properties=propertiesDict)
        except HTTPResponseError as e:
            if e.response.status_code == 502:
                print(f"Received 502 Bad Gateway error. Retrying... ({attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    print("Failed after multiple retries due to 502 Bad Gateway.")
                    raise
            else:
                raise
