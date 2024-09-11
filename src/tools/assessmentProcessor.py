import argparse
import json
import sys
import re
from datetime import datetime

def process_trivy(trivy_data):
    object_list = []

    if 'Resources' not in trivy_data:
        return
    
    trivyParse = trivy_data['Resources']

    for resourceObj in trivyParse:
        try:
            namespace = resourceObj.get('Namespace', 'N/A')
            kind = resourceObj.get('Kind', 'N/A')
            name = resourceObj.get('Name', 'N/A')
            resultsList = resourceObj.get('Results', [])
            
            resource_vulnerabilities = []
            resource_misconfigurations = []

            for result in resultsList:
                try:
                    resource = result.get('Target', 'N/A')
                    vulnerabilities = result.get('Vulnerabilities', [])
                    misconfigurations = result.get('Misconfigurations', [])

                    for misconfig in misconfigurations:
                        type = misconfig.get('Type', 'N/A')
                        ID = misconfig.get('ID', 'N/A')
                        title = misconfig.get('Title', 'N/A')
                        description = misconfig.get('Description', 'N/A')
                        message = misconfig.get('Message', 'N/A')
                        resolution = misconfig.get('Resolution', 'N/A')
                        status = misconfig.get('Status', 'N/A')

                        resource_misconfigurations.append({
                            'Type': type,
                            'ID': ID,
                            'Title': title,
                            'Description': description,
                            'Message': message,
                            'Resolution': resolution,
                            'Status': status,
                        })

                    for vuln in vulnerabilities:
                        cveID = vuln.get('VulnerabilityID', 'N/A')
                        cveURL = vuln.get('PrimaryURL', 'N/A')
                        cveSeverity = vuln.get('Severity', 'N/A')
                        
                        resource_vulnerabilities.append({
                            'Namespace': namespace,
                            'Resource': resource,
                            'CVE_ID': cveID,
                            'CVE_URL': cveURL,
                            'CVE_Severity': cveSeverity,
                        })
                except KeyError:
                    continue
            
            object_list.append({
                'Name': name,
                'Kind': kind,
                'Namespace': namespace,
                'Vulnerabilities': resource_vulnerabilities,
                'Misconfigurations': resource_misconfigurations,
            })

        except KeyError:
            continue
    return object_list

def process_kubescape(kubescape_data):
    object_list = []
    ks_resources = kubescape_data.get('resources', [])
    ks_summary = kubescape_data.get('summaryDetails', {})

    controls = ks_summary.get('controls', {})

    for control_name, control_details in controls.items():
        control_dict = {}
        try:
            control_dict['controlID'] = control_details.get('controlID')
            control_dict['status'] = control_details.get('statusInfo', {}).get('status')
            control_dict['name'] = control_details.get('name')
        except KeyError:
            continue
        
        if ks_resources:
            resource = ks_resources.pop(0)
            try:
                control_dict['resourceID'] = resource.get('resourceID', "None")
                control_dict['apiVersion'] = resource.get('object', {}).get('apiVersion', "None")
            except KeyError:
                continue

        object_list.append(control_dict)

    for resource in ks_resources:
        try:
            resource_dict = {
                'resourceID': resource.get('resourceID', "None"),
                'apiVersion': resource.get('object', {}).get('apiVersion', "None")
            }
            object_list.append(resource_dict)
        except KeyError:
            continue

    return object_list

def process_polaris(polaris_data):
    if polaris_data is None:
        return []
    
    object_list = []

    for result in polaris_data['Results']:
        name = result['Name']
        namespace = result['Namespace']
        kind = result['Kind']
        details = result['Results']
        for detail in details:
            if details[detail]['Success'] is False:
                rule = details[detail]['ID']
                violationType = details[detail]['Category']
                severity = details[detail]['Severity']

                object_list.append({
                    "Name": name,
                    "Namespace": namespace,
                    "Kind": kind,
                    "Results": {
                        "Rule": rule, 
                        "Violation Type": violationType,
                        "Severity": severity,
                    }
                })

    return object_list

def create_customer_object(trivy_data, kubescape_data, polaris_data, cluster_name):
    customer_object = {
        "Cluster Name": cluster_name,
        "Version": kubescape_data['clusterAPIServerInfo'].get('gitVersion'),
        "Cloud Provider": kubescape_data['clusterCloudProvider'],
        "kubescape": process_kubescape(kubescape_data),
        "trivy": process_trivy(trivy_data),
        "polaris": process_polaris(polaris_data),
    }
    return customer_object




def clean_answer(answer):
    # Remove any heading information from the answer
    cleaned_answer = re.sub(r'\n.*?________________$', '', answer, flags=re.DOTALL).strip()
    return cleaned_answer

def create_json_from_qa_interview(input_file):
    questions_and_answers = []

    with open(input_file, 'r') as file:
        data = file.read()

        # Regular expressions for matching questions and answers
        question_pattern = re.compile(r'Q: (.+?)\n')
        answer_pattern = re.compile(r'Notes?: (.+?)(?=\nQ:|\Z)', re.DOTALL)

        # Find all questions
        questions = question_pattern.findall(data)
        
        # Find all answers
        answers = answer_pattern.findall(data)
        
        # Clean up answers - remove excessive whitespace/newlines and headers
        answers = [clean_answer(answer.strip()) for answer in answers]

        # Combine questions and answers
        for question, answer in zip(questions, answers):
            questions_and_answers.append({
                "question": question,
                "answer": answer
            })

    return questions_and_answers