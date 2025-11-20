#!/usr/bin/env python3
"""
Script to download hierarchy template sheet and auto-fill with sample data
This generates a template based on created hierarchy and fills it with data from sample file
"""

from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId, BASE_URL
import time
import requests
import zipfile
import shutil
import os
import re


def fill_template_with_sample(template_file, hierarchy_type, sample_file="sample/sample.xlsx"):
    """
    Fill the downloaded template with data from sample file
    Keeps original template headers, only adds data rows with updated hierarchy codes
    """
    print(f"\nStep 6: Auto-filling template with sample data...")

    # Check if sample file exists
    if not os.path.exists(sample_file):
        print(f"⚠ Sample file not found at: {sample_file}")
        print(f"⚠ Skipping auto-fill. You can manually fill the template.")
        return template_file

    try:
        filled_file = template_file.replace('.xlsx', '_filled.xlsx')

        # Extract empty template (has correct headers)
        temp_template = 'output/temp_template'
        if os.path.exists(temp_template):
            shutil.rmtree(temp_template)
        os.makedirs(temp_template)

        with zipfile.ZipFile(template_file, 'r') as zip_ref:
            zip_ref.extractall(temp_template)

        # Extract sample file (has data)
        temp_sample = 'output/temp_sample'
        if os.path.exists(temp_sample):
            shutil.rmtree(temp_sample)
        os.makedirs(temp_sample)

        with zipfile.ZipFile(sample_file, 'r') as zip_ref:
            zip_ref.extractall(temp_sample)

        print(f"  ✓ Extracted template and sample files")

        # Read sample worksheet to get data rows (skip row 1 which is headers)
        sample_ws_path = os.path.join(temp_sample, 'xl', 'worksheets', 'sheet1.xml')
        with open(sample_ws_path, 'r', encoding='utf-8') as f:
            sample_ws = f.read()

        # Extract rows 2 onwards from sample (data rows only)
        data_rows = re.findall(r'<row r="(?:[2-9]|\d{2,})"[^>]*>.*?</row>', sample_ws, re.DOTALL)

        # Merge sharedStrings: keep template headers, append sample data strings
        sample_ss_path = os.path.join(temp_sample, 'xl', 'sharedStrings.xml')
        template_ss_path = os.path.join(temp_template, 'xl', 'sharedStrings.xml')

        with open(sample_ss_path, 'r', encoding='utf-8') as f:
            sample_ss = f.read()
        with open(template_ss_path, 'r', encoding='utf-8') as f:
            template_ss = f.read()

        # Extract string items from sample (skip first 11 headers, start from data)
        sample_strings = re.findall(r'<si>.*?</si>', sample_ss, re.DOTALL)
        # Sample has 11 headers (0-10), data starts at index 11
        data_strings = sample_strings[11:]  # Get only data strings

        # Update hierarchy codes in data strings only
        data_strings_updated = []
        for s in data_strings:
            updated = re.sub(r'\b[A-Z]+\d+_', f'{hierarchy_type}_', s)
            data_strings_updated.append(updated)

        # Insert data strings before closing </sst> tag in template
        template_ss_updated = template_ss.replace('</sst>', ''.join(data_strings_updated) + '</sst>')

        # Update count attributes
        template_count = int(re.search(r'uniqueCount="(\d+)"', template_ss).group(1))
        new_count = template_count + len(data_strings_updated)
        template_ss_updated = re.sub(r'uniqueCount="\d+"', f'uniqueCount="{new_count}"', template_ss_updated)
        template_ss_updated = re.sub(r'count="\d+"', f'count="{new_count}"', template_ss_updated)

        with open(template_ss_path, 'w', encoding='utf-8') as f:
            f.write(template_ss_updated)

        # Adjust string indices in data rows
        # Sample row references index N, but in merged file it should be N+1
        # (because template has 12 headers vs sample's 11)
        for i, row_str in enumerate(data_rows):
            # Find all string cell references like <v>11</v>, <v>12</v>, etc.
            def increment_index(match):
                old_index = int(match.group(1))
                new_index = old_index + 1
                return f'<v>{new_index}</v>'

            data_rows[i] = re.sub(r'<v>(\d+)</v>', increment_index, row_str)

        # Write worksheet with adjusted data rows
        template_ws_path = os.path.join(temp_template, 'xl', 'worksheets', 'sheet1.xml')
        with open(template_ws_path, 'r', encoding='utf-8') as f:
            template_ws = f.read()

        row1_end = template_ws.find('</row>') + len('</row>')
        data_rows_str = ''.join(data_rows)
        new_ws = template_ws[:row1_end] + data_rows_str + template_ws[row1_end:]

        # Update hierarchy codes in DATA rows only (not headers)
        new_ws = re.sub(r'\b[A-Z]+\d+_', f'{hierarchy_type}_', new_ws)

        with open(template_ws_path, 'w', encoding='utf-8') as f:
            f.write(new_ws)

        print(f"  ✓ Added {len(data_rows)} data rows with hierarchy type: {hierarchy_type}")
        print(f"  ✓ Headers preserved from template")
        print(f"  ✓ String indices adjusted for merged sharedStrings")

        # Repackage
        with zipfile.ZipFile(filled_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_template):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_template)
                    zip_ref.write(file_path, arcname)

        # Clean up
        shutil.rmtree(temp_template)
        shutil.rmtree(temp_sample)

        print(f"✓ Template auto-filled successfully!")
        print(f"  Filled file: {filled_file}")
        print(f"  Sample file used: {sample_file}\n")

        return filled_file

    except Exception as e:
        print(f"✗ Error auto-filling template: {str(e)}")
        print(f"⚠ Using original template file: {template_file}")
        return template_file


def generate_and_download_template(hierarchy_type):
    """Generate template and download it"""

    print(f"\n{'='*80}")
    print(f"HIERARCHY TEMPLATE DOWNLOAD WORKFLOW")
    print(f"{'='*80}\n")

    # Get authentication token
    print("Step 1: Authenticating...")
    token = get_auth_token("user")
    client = APIClient(token=token)
    print("✓ Authentication successful\n")

    # Step 2: Generate boundary data template
    print(f"Step 2: Generating template for hierarchy: {hierarchy_type}")
    payload = load_payload("boundary_management", "generate_data.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    url = f"/boundary-management/v1/_generate?tenantId={tenantId}&forceUpdate=true&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

    if response.status_code in [200, 202]:
        data = response.json()
        resource_details = data.get("ResourceDetails", [])
        if isinstance(resource_details, list) and resource_details:
            resource_id = resource_details[0].get("id")
        else:
            resource_id = data.get("ResourceDetails", {}).get("id")

        print(f"✓ Template generation triggered")
        print(f"  Resource ID: {resource_id}\n")

        # Save resource ID
        with open("output/ids.txt", "a") as f:
            f.write(f"Template Resource ID: {resource_id}\n")
    else:
        print(f"✗ Generation failed: {response.text}")
        return None

    # Step 3: Search for generated template (keep retrying until fileStoreid is available)
    print("Step 3: Searching for generated template...")
    print("  Waiting 30 seconds for template generation to start...")
    time.sleep(30)  # Wait 30 seconds before starting to poll

    file_store_id = None
    max_attempts = 10  # 10 attempts x 30 seconds = up to 300 seconds wait
    attempt = 0

    while attempt < max_attempts and not file_store_id:
        attempt += 1

        if attempt > 1:
            print(f"  Waiting 30 seconds before next attempt... (attempt {attempt}/{max_attempts})")
            time.sleep(30)  # Wait 30 seconds between retries

        # Search for generated template
        search_payload = load_payload("boundary_management", "generate_search.json")
        search_payload["RequestInfo"] = get_request_info(token)
        search_payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

        search_url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"
        search_response = client.post(search_url, search_payload)

        if search_response.status_code == 200:
            search_data = search_response.json()
            resources = search_data.get("GeneratedResource", [])

            if resources:
                latest_resource = resources[0]
                file_store_id = latest_resource.get("fileStoreid")  # lowercase 'id'
                status = latest_resource.get("status")

                if file_store_id:
                    print(f"✓ Template found!")
                    print(f"  Status = {status}")
                    print(f"  FileStore ID: {file_store_id}\n")

                    # Save fileStore ID
                    with open("output/ids.txt", "a") as f:
                        f.write(f"Template FileStore ID: {file_store_id}\n")
                    break  # Success - exit loop
                else:
                    # No fileStoreid yet, continue waiting
                    if attempt == 1:
                        print(f"  Template status: {status} (waiting for fileStoreid...)")

    if not file_store_id:
        print(f"✗ Template generation timeout after {max_attempts} attempts")
        print("  The template may still be generating. Please try again later.")
        return None

    # Step 4: Get download URL
    print("Step 4: Retrieving download URL...")
    download_url_endpoint = f"/filestore/v1/files/url?tenantId={tenantId}&fileStoreIds={file_store_id}"
    url_response = client.get(download_url_endpoint)

    if url_response.status_code == 200:
        url_data = url_response.json()
        file_store_ids = url_data.get("fileStoreIds", [])

        if file_store_ids:
            download_url = file_store_ids[0].get("url")
            print(f"✓ Download URL retrieved\n")
            print(f"{'='*80}")
            print(f"DOWNLOAD URL:")
            print(f"{'='*80}")
            print(f"{download_url}\n")

            # Save to file
            with open("output/template_download_url.txt", "w") as f:
                f.write(f"Hierarchy Type: {hierarchy_type}\n")
                f.write(f"FileStore ID: {file_store_id}\n")
                f.write(f"Download URL: {download_url}\n")

            print(f"✓ URL saved to: output/template_download_url.txt\n")

            # Step 5: Download the file
            print("Step 5: Downloading template file...")
            try:
                file_response = requests.get(download_url, verify=False)
                if file_response.status_code == 200:
                    filename = f"output/hierarchy_template_{hierarchy_type}.xlsx"
                    with open(filename, "wb") as f:
                        f.write(file_response.content)

                    print(f"✓ Template downloaded successfully!")
                    print(f"  File saved to: {filename}")
                    print(f"  File size: {len(file_response.content)} bytes\n")

                    # Step 6: Auto-fill template with sample data
                    filled_filename = fill_template_with_sample(filename, hierarchy_type)

                    print(f"{'='*80}")
                    print(f"NEXT STEPS:")
                    print(f"{'='*80}")
                    print(f"1. Review the filled file: {filled_filename}")
                    print(f"2. Modify boundary data if needed (codes, names, coordinates, etc.)")
                    print(f"3. Upload using test_upload_file test")
                    print(f"4. Process using test_process_boundary_data test\n")

                    return filled_filename
                else:
                    print(f"✗ Download failed: HTTP {file_response.status_code}")
            except Exception as e:
                print(f"✗ Download error: {str(e)}")
        else:
            print(f"✗ No download URL found")
    else:
        print(f"✗ Failed to retrieve download URL: {url_response.text}")

    return None

if __name__ == "__main__":
    # Read the latest hierarchy type
    try:
        hierarchy_type = None
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()

        if not hierarchy_type:
            print("✗ No hierarchy type found. Please run test_create_boundary_hierarchy first.")
            exit(1)

        print(f"Using hierarchy type: {hierarchy_type}\n")
        downloaded_file = generate_and_download_template(hierarchy_type)

        if downloaded_file:
            print(f"\n{'='*80}")
            print(f"SUCCESS! Filled template ready at: {downloaded_file}")
            print(f"{'='*80}")
            print(f"The template has been auto-filled with sample data.")
            print(f"Hierarchy type codes updated to: {hierarchy_type}")
            print(f"Ready for upload and processing!")
            print(f"{'='*80}\n")
        else:
            print(f"\n{'='*80}")
            print(f"Template generation in progress. Run this script again in a few minutes.")
            print(f"{'='*80}\n")

    except FileNotFoundError:
        print("✗ No ids.txt file found. Please run test_create_boundary_hierarchy first.")
        exit(1)
