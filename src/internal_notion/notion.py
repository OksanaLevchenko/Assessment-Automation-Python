from datetime import datetime
from notion_client import Client

def get_formatted_date() -> str:
    now = datetime.now()  # Get the current date and time
    return now.strftime("%B %d, %Y - %I:%M %p")

def create_title_block(content: str, level: int = 2, color: str = "default") -> dict:
    return {
        "object": "block",
        f"type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": content},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": color
                    }
                }
            ]
        }
    }

def create_paragraph_block(content: str = "", color: str = "default") -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "color": color
        }
    }

def create_property_block(name: str, options: list) -> dict:
    return {
        "name": name,
        "type": "multi_select",
        "multi_select": {"options": [{"name": opt_name, "color": opt_color} for opt_name, opt_color in options]}
    }

def create_assessment_page(notion_session: Client, customerID: str):
    formatDate = get_formatted_date()
    parent = {"page_id": customerID}
    properties = {
        "title": {
            "title": [{"text": {"content": f"Assessment - {formatDate}"}}]
        }
    }
    return notion_session.pages.create(parent=parent, properties=properties)

def createAssessmentDB(notion_session, pageId):
    formatDate = get_formatted_date()
    parentDict = {"type": "page_id", "page_id": pageId}
    titleDict = [{"type": "text", "text": {"content": f"Assessment - {formatDate}"}}]
    propertiesDict = {
        "Resource Name": {"title": {}},  # This is a required property
        "Namespace": {"rich_text": {}},
        "Resource Type": {"rich_text": {}},
        "Violation Severity": create_property_block("Violation Severity", [("warning", "yellow"), ("danger", "red")]),
        "Rule Violated": {"rich_text": {}},
        "Violation Type": {"rich_text": {}},
        "Violation Message": {"rich_text": {}},
        "Reviewed": {"checkbox": {}},
        "Data Source": create_property_block("Data Source", [("polaris", "blue"), ("kubescape", "yellow"), ("trivy", "red")])
    }
    return notion_session.databases.create(parent=parentDict, title=titleDict, properties=propertiesDict)

def create_toggle_block(heading, qas):
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": heading}}],
            "children": [
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": f"Q: {qa['question']}\nA: {qa['answer']}"}}]}
                }
                for qa in qas
            ]
        }
    }

def create_table_block(rows):
    table_rows = [
        create_table_row(row)
        for row in rows
    ]
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": 3,
            "has_column_header": True,
            "has_row_header": False,
            "children": table_rows
        }
    }

def create_table_row(cells):
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [[{"type": "text", "text": {"content": cell}}] for cell in cells]
        }
    }

def create_assessment_block(notion_client: Client, block_id: str, assessment_data: dict, deprecated_apis: list):
    blocks = [
        create_title_block("Executive Summary"),
        create_paragraph_block(color="gray_background"),
        create_title_block("Key findings"),
        create_paragraph_block(color="gray_background"),
        create_title_block("Recommendations"),
        create_paragraph_block(color="gray_background"),
        create_title_block("Overall Platform Readiness"),
        ## Insert DB /  Table for platform readiness
        create_title_block("Q&A Review"),
    ]
    
    blocks.extend(create_toggle_block(header, qas) for header, qas in assessment_data.items())
    
    blocks.append(create_title_block("Upgrade compatibility check"))

    if not deprecated_apis:
        blocks.append(create_paragraph_block("No deprecated APIs are running in this cluster until to 1.29"))
    else:
        table_rows = [["Deprecated Version", "New Version", "Available In"]] + [
            [api.get('deprecated_version', ""), api.get('new_version', ""), api.get('available_in', "")]
            for api in deprecated_apis
        ]
        blocks.append(create_table_block(table_rows))
    
    blocks.append(create_title_block("Automated Assessment Data"))
    blocks.append(create_paragraph_block())
    
    return notion_client.blocks.children.append(block_id=block_id, children=blocks)