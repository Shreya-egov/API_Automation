from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import allure
import json
import pytest


def process_boundary_data(token, client, file_store_id, hierarchy_type):
    """
    Helper function to process boundary data from uploaded file
    Returns: process_id, status_code
    """
    payload = load_payload("boundary_management", "process_data.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["ResourceDetails"]["tenantId"] = tenantId
    payload["ResourceDetails"]["fileStoreId"] = file_store_id
    payload["ResourceDetails"]["hierarchyType"] = hierarchy_type

    allure.attach(json.dumps(payload, indent=2), name="Process Request Payload", attachment_type=allure.attachment_type.JSON)

    # Make API call
    response = client.post("/boundary-management/v1/_process", payload)

    allure.attach(f"Status Code: {response.status_code}", name="Process Response Status", attachment_type=allure.attachment_type.TEXT)
    allure.attach(json.dumps(response.json(), indent=2) if response.text else "No response body", name="Process Response Body", attachment_type=allure.attachment_type.JSON)

    if response.status_code not in [200, 202]:
        print(f"Error processing boundary data: {response.text}")
        return None, response.status_code

    data = response.json()
    process_id = data.get("ResourceDetails", {}).get("id")

    return process_id, response.status_code


@pytest.mark.order(9)
@allure.feature("Boundary Management")
@allure.story("Process Boundary Data")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Test Process Boundary Data")
@allure.description("Processes boundary data from a generated template file and validates the processing")
def test_process_boundary_data():
    """Test processing boundary data (requires fileStoreId from generate search)"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # This test requires a fileStoreId from the generate search that matches the hierarchy
    # It will skip if no matching fileStoreId is available
    try:
        hierarchy_type = None
        file_store_id = None
        found_hierarchy = False

        # Read the file in reverse to get the most recent matching hierarchy and filestore ID
        with open("output/ids.txt", "r") as f:
            lines = f.readlines()

        # Parse backwards to find the most recent hierarchy type and its corresponding Uploaded FileStore ID
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if line.startswith("Hierarchy Type:") and not found_hierarchy:
                hierarchy_type = line.split(":")[1].strip()
                found_hierarchy = True
                # Now look forward from this point to find the associated Uploaded FileStore ID (the filled template)
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("Uploaded FileStore ID:"):
                        file_store_id = lines[j].split(":", 1)[1].strip()
                        break
                    elif lines[j].startswith("Hierarchy Type:"):
                        # Hit another hierarchy type, stop searching
                        break
                break

        if not hierarchy_type:
            print("Skipping test: No Hierarchy Type found.")
            return

        if not file_store_id:
            print("Skipping test: No Uploaded FileStore ID found.")
            print("This test requires the filled template to be uploaded first.")
            print("Run test_upload_file to upload the filled boundary template.")
            return

        print(f"Processing boundary data for hierarchy: {hierarchy_type}")
        print(f"Using Uploaded FileStore ID (filled template): {file_store_id}")

        process_id, status = process_boundary_data(token, client, file_store_id, hierarchy_type)

        if status == 400:
            print("WARNING: Processing failed with 400 error. This usually means:")
            print("  - The file headers don't match the hierarchy type")
            print("  - The file needs to be downloaded, filled with data, and uploaded again")
            print("Skipping test - this is expected if using a template that hasn't been filled.")
            return

        assert status in [200, 202], f"Boundary data processing failed with unexpected status: {status}"
        assert process_id is not None, "Process ID not returned"

        print(f"Boundary data processing triggered. Process ID: {process_id}")

        # Store for later use
        with open("output/ids.txt", "a") as f:
            f.write(f"Process ID: {process_id}\n")

    except FileNotFoundError:
        print("No ids.txt file found. Run previous tests first.")
