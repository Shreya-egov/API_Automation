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
    Replaces any existing hierarchy type codes with the new hierarchy type
    """
    print(f"\nStep 6: Auto-filling template with sample data...")

    # Check if sample file exists
    if not os.path.exists(sample_file):
        print(f"⚠ Sample file not found at: {sample_file}")
        print(f"⚠ Skipping auto-fill. You can manually fill the template.")
        return template_file

    try:
        filled_file = template_file.replace('.xlsx', '_filled.xlsx')

        # Create a temporary directory to extract and modify
        temp_dir = 'output/temp_xlsx'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Extract sample file
        with zipfile.ZipFile(sample_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        print(f"  ✓ Extracted sample file")

        # Read and modify shared strings - replace any hierarchy type codes with new one
        shared_strings_path = os.path.join(temp_dir, 'xl', 'sharedStrings.xml')
        if os.path.exists(shared_strings_path):
            with open(shared_strings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace old hierarchy type patterns (like TETE5) with new hierarchy type
            # Pattern matches WORD_WORD format (old hierarchy type codes)
            content = re.sub(r'\b[A-Z]+\d+_', f'{hierarchy_type}_', content)

            with open(shared_strings_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  ✓ Updated localization strings with hierarchy type: {hierarchy_type}")

        # Read and modify worksheet
        worksheet_path = os.path.join(temp_dir, 'xl', 'worksheets', 'sheet1.xml')
        if os.path.exists(worksheet_path):
            with open(worksheet_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace old hierarchy type patterns with new one
            content = re.sub(r'\b[A-Z]+\d+_', f'{hierarchy_type}_', content)

            with open(worksheet_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  ✓ Updated worksheet data")

        # Create new xlsx file
        with zipfile.ZipFile(filled_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)

        # Clean up
        shutil.rmtree(temp_dir)

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

    # Step 3: Wait and search for generated template
    print("Step 3: Waiting for template generation (checking every 3 seconds)...")
    max_attempts = 20
    attempt = 0
    file_store_id = None

    while attempt < max_attempts:
        attempt += 1
        time.sleep(3)

        # Search for generated template
        search_payload = load_payload("boundary_management", "generate_search.json")
        search_payload["RequestInfo"] = get_request_info(token)
        search_payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

        search_url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"
        search_response = client.post(search_url, search_payload)

        if search_response.status_code == 200:
            search_data = search_response.json()
            resources = search_data.get("ResourceDetails", [])

            if resources:
                latest_resource = resources[0]
                file_store_id = latest_resource.get("fileStoreId")
                status = latest_resource.get("status")

                print(f"  Attempt {attempt}: Status = {status}")

                if file_store_id:
                    print(f"✓ Template generated successfully!")
                    print(f"  FileStore ID: {file_store_id}\n")

                    # Save fileStore ID
                    with open("output/ids.txt", "a") as f:
                        f.write(f"Template FileStore ID: {file_store_id}\n")
                    break

        if attempt == max_attempts:
            print(f"✗ Template generation timeout after {max_attempts} attempts")
            return None

    if not file_store_id:
        print("✗ No template file generated yet")
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
