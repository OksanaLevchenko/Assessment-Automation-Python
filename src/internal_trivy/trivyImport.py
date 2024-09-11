from src.internal_notion.notionInsertToDB import InsertToAssessmentDB
import json
def importTrivyData(notionSession, trivyResults, dbID):
    source = "trivy"
    
    # Check if trivyResults is a list
    if not isinstance(trivyResults, list):
        print("Expected trivyResults to be a list, but got something else.")
        return
    
    for resultItem in trivyResults:
        try:
            trivyParse = resultItem['Results']
        except KeyError:
            print("Invalid JSON structure: 'Results' key not found in one of the items.")
            continue

        for result in trivyParse:
            try:
                namespace = result.get('Class', 'Unknown')
                resource = result.get('Target', 'Unknown')
                vulnerabilities = result.get('Vulnerabilities', [])
            except KeyError as e:
                print(f"KeyError: {e} in result item {result}")
                continue
            
            for vuln in vulnerabilities:
                try:
                    cveID = vuln.get('VulnerabilityID', 'Unknown')
                    cveURL = vuln.get('PrimaryURL', '')
                    cveSeverity = vuln.get('Severity', 'Unknown')
                    pkgID = vuln.get('PkgID', 'Unknown')
                    pkgName = vuln.get('PkgName', 'Unknown')
                    installedVersion = vuln.get('InstalledVersion', 'Unknown')
                    layer = vuln.get('Layer', {})
                    digest = layer.get('Digest', '')
                    diffID = layer.get('DiffID', '')
                    severitySource = vuln.get('SeveritySource', 'Unknown')
                    kind = ''
                    
                    InsertToAssessmentDB(
                        notionSession, dbID, resource, namespace, kind, cveID,
                        'CVE', cveSeverity, cveURL, source
                    )
                except Exception as e:
                    print(f"Error processing vulnerability: {e}")
                    continue