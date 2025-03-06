# Email Parser

# README #
"""
This is a Python script that processes different types of email files (like .eml, .msg) and extracts key indicators such as SPF, DKIM, DMARC status, source IP, destination IP, and other email headers.

How It Works
Email Parsing:
	The script reads email files (.eml or .msg) and parses their headers.
	It uses Python's email module to extract email header information.
Indicator Extraction:
	SPF, DKIM, DMARC, source IP, and destination email are extracted from the email headers.
	Regex is used to find IP addresses in the Received headers.
Directory Support:
	It recursively processes all files in a specified directory to extract indicators.
Command-Line Usage:
	Run the script using a command like:
	<python EmailParser.py /path/to/email/files>
Output
	The script prints the extracted indicators for each processed email file. You can modify it to save the results to a file or database if needed.
"""

import os
import email
import re
from email.parser import Parser
from email.policy import default
from typing import Dict, List

# Function to extract key indicators from email headers
def extract_email_indicators(headers: Dict[str, str]) -> Dict[str, str]:
    indicators = {}

    # Extract SPF, DKIM, DMARC status
    indicators['SPF'] = headers.get('Received-SPF', 'Not Found')
    indicators['DKIM'] = headers.get('Authentication-Results', 'Not Found')
    indicators['DMARC'] = headers.get('Authentication-Results', 'Not Found')

    # Extract source and destination IPs
    received_headers = headers.get('Received', '')
    source_ips = re.findall(r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b', received_headers)
    indicators['Source IP'] = source_ips[0] if source_ips else 'Not Found'

    to_header = headers.get('To', '')
    indicators['Destination Email'] = to_header

    return indicators

# Function to parse email file
def parse_email(file_path: str) -> Dict[str, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            email_content = f.read()
            email_message = Parser(policy=default).parsestr(email_content)
            headers = dict(email_message)
            return headers
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

# Function to process email files in a directory
def process_email_files(directory: str):
    results = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.eml', '.msg')):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")

                headers = parse_email(file_path)
                if headers:
                    indicators = extract_email_indicators(headers)
                    results.append({"file": file, "indicators": indicators})

    return results

# Function to print extracted indicators
def print_results(results: List[Dict]):
    for result in results:
        print(f"\\nFile: {result['file']}")
        for key, value in result['indicators'].items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract email indicators from email files.")
    parser.add_argument("directory", help="Path to the directory containing email files.")
    args = parser.parse_args()

    email_results = process_email_files(args.directory)
    print_results(email_results)
