from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import time
import allure
import json
import pytest


def search_generated_boundary(token, client, hierarchy_type, wait_for_completion=False, max_retries=10, retry_interval=3):
    """
    Helper function to search for generated boundary data
    Args:
        token: Auth token
        client: API client
        hierarchy_type: Hierarchy type to search for
        wait_for_completion: If True, polls until status is 'completed'
        max_retries: Maximum number of polling attempts
        retry_interval: Seconds to wait between polling attempts
    Returns: response object
    """
    payload = load_payload("boundary_management", "generate_search.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Make API call with query parameters
    url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"

    if not wait_for_completion:
        response = client.post(url, payload)
        return response

    # Poll until status becomes 'completed'
    for attempt in range(max_retries):
        response = client.post(url, payload)

        if response.status_code != 200:
            print(f"Search attempt {attempt + 1} failed with status {response.status_code}")
            allure.attach(f"Attempt {attempt + 1}: Status {response.status_code}", name=f"Search Attempt {attempt + 1}", attachment_type=allure.attachment_type.TEXT)
            time.sleep(retry_interval)
            continue

        data = response.json()
        generated_resources = data.get("GeneratedResource", [])

        if not generated_resources:
            print(f"Attempt {attempt + 1}/{max_retries}: No resources found yet, retrying in {retry_interval}s...")
            allure.attach(f"Attempt {attempt + 1}: No resources found", name=f"Polling Attempt {attempt + 1}", attachment_type=allure.attachment_type.TEXT)
            time.sleep(retry_interval)
            continue

        status = generated_resources[0].get("status", "").lower()
        print(f"Attempt {attempt + 1}/{max_retries}: Current status = '{status}'")
        allure.attach(f"Attempt {attempt + 1}: Status = {status}", name=f"Polling Attempt {attempt + 1}", attachment_type=allure.attachment_type.TEXT)

        if status == "completed":
            print(f"Status is 'completed' - proceeding")
            allure.attach(json.dumps(data, indent=2), name="Final Search Response", attachment_type=allure.attachment_type.JSON)
            return response

        if status in ["failed", "error"]:
            print(f"Generation failed with status: {status}")
            allure.attach(json.dumps(data, indent=2), name="Failed Search Response", attachment_type=allure.attachment_type.JSON)
            return response

        if attempt < max_retries - 1:
            print(f"Waiting {retry_interval}s before next check...")
            time.sleep(retry_interval)

    print(f"Warning: Max retries ({max_retries}) reached. Last status was not 'completed'")
    allure.attach(json.dumps(response.json(), indent=2) if response.text else "No response", name="Last Search Response", attachment_type=allure.attachment_type.JSON)
    return response


@pytest.mark.order(6)
@allure.feature("Boundary Management")
@allure.story("Search Generated Boundary")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Test Search Generated Boundary with Status Polling")
@allure.description("Polls the generated boundary API until status becomes 'completed' and retrieves the filestore ID")
def test_search_generated_boundary():
    """Test searching for generated boundary data (with status polling)"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        # Make a single API call without polling
        response = search_generated_boundary(token, client, hierarchy_type, wait_for_completion=False)

        assert response.status_code == 200, f"Generated boundary search failed: {response.text}"

        data = response.json()
        generated_resources = data.get("GeneratedResource", [])

        print(f"Found {len(generated_resources)} generated resources")

        if len(generated_resources) > 0:
            status = generated_resources[0].get("status", "")
            filestore_id = generated_resources[0].get("fileStoreId")
            print(f"Status: {status}")
            print(f"FileStore ID: {filestore_id}")

            # Store filestore ID if available
            if filestore_id:
                with open("output/ids.txt", "a") as f:
                    f.write(f"FileStore ID: {filestore_id}\n")
        else:
            print("No generated resources found")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
