#!/usr/bin/env python3
"""
Quick script to upload the filled template
"""
from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.config import tenantId, BASE_URL
import os
import requests
import json

def upload_filled_template():
    # Get authentication token
    print("Step 1: Authenticating...")
    token = get_auth_token("user")
    print("✓ Authentication successful\n")

    # Read the hierarchy type from file
    hierarchy_type = None
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    if not hierarchy_type:
        print("✗ No hierarchy type found")
        return None

    file_path = f"output/hierarchy_template_{hierarchy_type}_filled.xlsx"

    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return None

    print(f"Step 2: Uploading file: {file_path}")
    print(f"Hierarchy Type: {hierarchy_type}\n")

    # Prepare multipart form data
    filename = os.path.basename(file_path)
    files = {
        'file': (filename, open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'tenantId': tenantId,
        'module': 'HCM-ADMIN-CONSOLE'
    }

    # Make request
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/filestore/v1/files"

    print(f"Uploading to: {url}")
    print(f"Tenant ID: {tenantId}")
    print(f"Module: HCM-ADMIN-CONSOLE")
    print(f"File size: {os.path.getsize(file_path)} bytes\n")

    response = requests.post(
        url,
        files=files,
        data=data,
        headers=headers,
        verify=False
    )

    files['file'][1].close()

    print(f"Response Status: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    print()

    if response.status_code in [200, 201]:
        data = response.json()
        file_store_id = data.get("files", [])[0].get("fileStoreId") if data.get("files") else None

        if file_store_id:
            print(f"✓ Upload successful!")
            print(f"FileStore ID: {file_store_id}\n")

            # Store for later use
            with open("output/ids.txt", "a") as f:
                f.write(f"Uploaded FileStore ID: {file_store_id}\n")

            return file_store_id
        else:
            print("✗ No fileStoreId in response")
            return None
    else:
        print(f"✗ Upload failed")
        return None


if __name__ == "__main__":
    upload_filled_template()
