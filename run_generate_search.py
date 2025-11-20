#!/usr/bin/env python3
"""Script to run generate search API and display response"""

from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import json

def main():
    # Get auth token
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break
    except FileNotFoundError:
        print("Error: output/ids.txt not found. Run boundary hierarchy create test first.")
        return

    # Load payload
    payload = load_payload("boundary_management", "generate_search.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Build URL
    url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"

    print("=" * 80)
    print("GENERATE SEARCH API REQUEST")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Hierarchy Type: {hierarchy_type}")
    print(f"Tenant ID: {tenantId}")
    print("\nRequest Payload:")
    print(json.dumps(payload, indent=2))

    # Make API call
    response = client.post(url, payload)

    print("\n" + "=" * 80)
    print("GENERATE SEARCH API RESPONSE")
    print("=" * 80)
    print(f"Status Code: {response.status_code}")
    print("\nResponse Body:")
    print(json.dumps(response.json(), indent=2))

    # Parse response
    data = response.json()
    generated_resources = data.get("GeneratedResource", [])

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Resources Found: {len(generated_resources)}")

    if generated_resources:
        for i, resource in enumerate(generated_resources, 1):
            print(f"\nResource {i}:")
            print(f"  ID: {resource.get('id')}")
            print(f"  Status: {resource.get('status')}")
            print(f"  FileStore ID: {resource.get('fileStoreId')}")
            print(f"  Hierarchy Type: {resource.get('hierarchyType')}")
            print(f"  Tenant ID: {resource.get('tenantId')}")
    else:
        print("No generated resources found.")
        print("\nNote: This might mean:")
        print("  1. Boundary data generation hasn't been triggered yet")
        print("  2. Generation is still in progress")
        print("  3. Generation failed")

if __name__ == "__main__":
    main()
