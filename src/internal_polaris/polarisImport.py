from src.internal_notion.notionInsertToDB import InsertToAssessmentDB
import json
def importPolarisData(notionSession, polarisResults, dbID):
    source = "polaris"
    for result in polarisResults['Results']:
        # print (result)
        name = result['Name']
        namespace = result['Namespace']
        kind = result['Kind']
        details = result['Results']
        for detail in details:
            if details[detail]['Success'] is False:
                rule = details[detail]['ID']
                violationType = details[detail]['Category']
                severity = details[detail]['Severity']
                message = details[detail]['Message']
                InsertToAssessmentDB(notionSession, dbID, name, namespace, kind, rule,
                                                      violationType, severity, message, source)
