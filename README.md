# Security Assessment Automation Script

## Overview

This project automates the process of collecting, processing, and reporting security scan results from various sources (Trivy, Polaris, Kubescape) into a Notion database. It aims to simplify the integration of security vulnerabilities into a centralized dashboard for better tracking, reporting, and remediation. The script is designed to streamline security assessment workflows, ensuring fast and efficient analysis of security vulnerabilities across Kubernetes environments.

---

## Key Features

- **Multi-tool Integration**: The script supports data ingestion from three major security scanning tools: Trivy, Polaris, and Kubescape.
- **Automated CVE Analysis**: The script automatically counts CVEs by severity (HIGH, MEDIUM, LOW, CRITICAL) to give you an overview of the security posture.
- **Notion Integration**: Results from the security scans are automatically imported into a Notion database for easy reporting and tracking.
- **Scalability**: The tool is designed to process large-scale JSON files concurrently, improving efficiency and reducing processing time.
- **Error Handling**: Includes built-in validation and error handling to ensure smooth operation.

---

## Prerequisites

Before you can use the script, ensure the following requirements are met:

### System Requirements

- **Python 3.6+**: The script is compatible with Python 3.6 and higher.
- **Notion API Key**: Required to authenticate and interact with the Notion API.

### Dependencies

Install the necessary Python packages by running:

```bash
pip install -r requirements.txt
```

### Input Files

The script processes security scan results in JSON format. The following tools are supported:

- **Trivy**: JSON scan results from the Trivy vulnerability scanner.
- **Polaris**: JSON scan results from the Polaris security scanner.
- **Kubescape**: JSON scan results from the Kubescape security scanner.

You must have these JSON files generated from each respective tool before running the script.

---

## Setup Instructions

### Step 1: Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/your-repository.git
```

### Step 2: Prepare the JSON Files

Ensure you have the following JSON files ready:

- **Trivy Scan Results**: JSON file containing the output from Trivy.
- **Polaris Scan Results** (Optional): JSON file containing the output from Polaris.
- **Kubescape Scan Results** (Optional): JSON file containing the output from Kubescape.

These files should be generated using the respective security tools.

---

## Running the Script

To run the script, use the following command:

```bash
python main.py -t /path/to/trivy/json/files -p /path/to/polaris/json/file -k /path/to/kubescape/json/file -c "Customer Name" -K "your_notion_api_key"
```

### Command Line Arguments:

- `t, --trivy`: **Required**. Path to the directory containing Trivy JSON files.
- `p, --polaris`: **Optional**. Path to the Polaris JSON file.
- `k, --kubescape`: **Optional**. Path to the Kubescape JSON file.
- `c, --customer`: **Required**. Customer name for whom the assessment is being generated.
- `K, --notion-key`: **Required**. Notion API key used for authentication with the Notion API.

### Output

1. **Merged JSON File**: The script will merge Trivy, Polaris, and Kubescape data into a single combined JSON file, saved in the `data/script_outputs/{customer_name}` directory.
2. **CVE Count Report**: The script will print the number of CVEs categorized by severity (e.g., HIGH, CRITICAL, etc.) in the terminal.
3. **Notion Database**: The script will create a new Notion page and database for the specified customer. It will import the security scan data (from Trivy, Polaris, Kubescape) into this Notion database.