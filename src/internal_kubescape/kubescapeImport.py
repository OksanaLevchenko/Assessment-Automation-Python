from src.internal_notion.notionInsertToDB import InsertToAssessmentDB
import json
import re

def importKubescapeData(notionSession, kubescapeResults, dbID):
    source = "kubescape"
    for resource in kubescapeResults['results']:
        resourceNameRegex = re.search(r"([^/]+$)", resource['resourceID'])
        if resourceNameRegex:
            resourceName = resourceNameRegex.group(0)

        resourceTypeRegex = re.search(r"/(\w+)/[^/]*$", resource['resourceID'])
        if resourceTypeRegex:
            resourceTypeString = resourceTypeRegex.group(0)
            resourceTypeArray = resourceTypeString.split("/")
            resourceType = resourceTypeArray[1] if len(resourceTypeArray) > 1 else ''

        for control in resource['controls']:
            statusDict = control['status']
            status = statusDict['status']
            subStatus = statusDict.get('subStatus')

            if status == 'failed':
                controlID = control['controlID']
                controlName = control['name']
                severity = 'danger'
                namespace = ''
                violationType = ''
                InsertToAssessmentDB(
                    notionSession, dbID, resourceName, namespace, resourceType, controlID,
                    violationType, severity, controlName, source
                )
            elif subStatus is not None:
                controlID = control['controlID']
                controlName = control['name']
                severity = 'warning'
                namespace = ''
                violationType = ''
                InsertToAssessmentDB(
                    notionSession, dbID, resourceName, namespace, resourceType, controlID,
                    violationType, severity, controlName, source
                )
            else:
                continue
