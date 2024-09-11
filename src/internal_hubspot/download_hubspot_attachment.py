import os
import requests
import webbrowser
from urllib.parse import urlparse, parse_qs
from hubspot import HubSpot
from hubspot.cms.source_code.api_client import ApiClient
from hubspot.cms.source_code.configuration import Configuration

def extract_filename(file_url):
    parsed_url = urlparse(file_url)
    query_params = parse_qs(parsed_url.query)
    filename = query_params.get('filename', [None])[0]
    if not filename:
        filename = os.path.basename(parsed_url.path)
    return filename

def download_attachment(file_url, api_key):
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(file_url, allow_redirects=True)
        response.raise_for_status()
        
        if response.url != file_url:
            print(f"Redirected to:\n {response.url}")
            webbrowser.open(response.url)  # Open the redirected URL in the default web browser
        else:
            print("No redirection occurred, and direct download is not supported via this method.")
            print(f"Please manually visit: {file_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

def get_file_details(file_id, api_key):
    url = f"https://api.hubapi.com/filemanager/api/v2/files/{file_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file details: {e}")
        return None

def get_engagements(ticket_id, api_key):
    url = f"https://api.hubapi.com/engagements/v1/engagements/associated/ticket/{ticket_id}/paged"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": 100}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching engagement details: {e}")
        return None

def get_hubspot_attachments():
    hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
    if hubspot_api_key is None:
        hubspot_api_key = input("Please enter the HubSpot API Key: ")
    
    ticket_id = os.getenv("HUBSPOT_TICKET_ID")
    if ticket_id is None:
        ticket_id = input("Please enter the HubSpot Ticket ID: ")


    configuration = Configuration()
    configuration.access_token = hubspot_api_key
    api_client = ApiClient(configuration=configuration)

    engagements = get_engagements(ticket_id, hubspot_api_key)
    if not engagements:
        return

    for engagement in engagements.get('results', []):
        attachments = engagement.get('attachments', [])
        for attachment in attachments:
            attachment_id = attachment.get('id')
            if attachment_id:
                file_details = get_file_details(attachment_id, hubspot_api_key)
                if file_details:
                    file_url = file_details.get('url', '')
                    download_url = file_details.get('directUrl', file_url) # Adjust this line based on actual response field
                    if download_url:
                        download_attachment(download_url, hubspot_api_key)

# Run the function to get and process attachments
get_hubspot_attachments()
