#!/usr/bin/env python3
"""
Quick script to process boundary data with the corrected template
"""
from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import json

def process_boundary():
    # Get authentication token
    print("Step 1: Authenticating...")
    token = get_auth_token("user")
    client = APIClient(token=token)
    print("✓ Authentication successful\n")

    # Read hierarchy type and latest uploaded fileStoreId
    hierarchy_type = None
    file_store_id = None

    with open("output/ids.txt", "r") as f:
        lines = f.readlines()

    # Get last hierarchy type
    for line in lines:
        if line.startswith("Hierarchy Type:"):
            hierarchy_type = line.split(":")[1].strip()

    # Get last Uploaded FileStore ID
    for line in reversed(lines):
        if line.startswith("Uploaded FileStore ID:"):
            file_store_id = line.split(":", 1)[1].strip()
            break

    print(f"Hierarchy Type: {hierarchy_type}")
    print(f"FileStore ID (latest upload): {file_store_id}\n")

    # Process boundary data
    print("Step 2: Processing boundary data...")
    payload = load_payload("boundary_management", "process_data.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["ResourceDetails"]["tenantId"] = tenantId
    payload["ResourceDetails"]["fileStoreId"] = file_store_id
    payload["ResourceDetails"]["hierarchyType"] = hierarchy_type

    print(f"Request Payload:")
    print(json.dumps(payload, indent=2))
    print()

    # Make API call
    response = client.post("/boundary-management/v1/_process", payload)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2) if response.text else "No response body")
    print()

    if response.status_code in [200, 202]:
        data = response.json()
        process_id = data.get("ResourceDetails", {}).get("id")

        print(f"✓ Processing started successfully!")
        print(f"Process ID: {process_id}\n")

        # Store for later use
        with open("output/ids.txt", "a") as f:
            f.write(f"Process ID: {process_id}\n")

        return process_id
    else:
        print(f"✗ Processing failed")
        return None


if __name__ == "__main__":
    process_boundary()
