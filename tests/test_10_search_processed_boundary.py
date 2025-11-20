from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import time
import allure
import json
import pytest


def search_processed_boundary(token, client, process_id, wait_for_completion=False, max_retries=10, retry_interval=3):
    """
    Helper function to search for processed boundary data
    Args:
        token: Auth token
        client: API client
        process_id: Process ID to search for
        wait_for_completion: If True, polls until status is 'completed'
        max_retries: Maximum number of polling attempts
        retry_interval: Seconds to wait between polling attempts
    Returns: response object
    """
    payload = load_payload("boundary_management", "process_search.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["SearchCriteria"]["id"] = [process_id]
    payload["SearchCriteria"]["tenantId"] = tenantId

    if not wait_for_completion:
        response = client.post("/boundary-management/v1/_process-search", payload)
        return response

    # Poll until status becomes 'completed'
    for attempt in range(max_retries):
        response = client.post("/boundary-management/v1/_process-search", payload)

        if response.status_code != 200:
            print(f"Search attempt {attempt + 1} failed with status {response.status_code}")
            time.sleep(retry_interval)
            continue

        data = response.json()
        resource_details = data.get("ResourceDetails", [])

        if not resource_details:
            print(f"Attempt {attempt + 1}/{max_retries}: No resources found yet, retrying in {retry_interval}s...")
            time.sleep(retry_interval)
            continue

        status = resource_details[0].get("status", "").lower()
        print(f"Attempt {attempt + 1}/{max_retries}: Current status = '{status}'")

        if status == "completed":
            print(f"Status is 'completed' - proceeding")
            return response

        if status in ["failed", "error"]:
            print(f"Processing failed with status: {status}")
            return response

        if attempt < max_retries - 1:
            print(f"Waiting {retry_interval}s before next check...")
            time.sleep(retry_interval)

    print(f"Warning: Max retries ({max_retries}) reached. Last status was not 'completed'")
    return response


@pytest.mark.order(10)
@allure.feature("Boundary Management")
@allure.story("Search Processed Boundary")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Test Search Processed Boundary with Status Polling")
@allure.description("Polls the processed boundary API until status becomes 'completed' and retrieves the processed filestore ID")
def test_search_processed_boundary():
    """Test searching for processed boundary data (with status polling)"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the process ID from file
    try:
        process_id = None

        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Process ID:"):
                    process_id = line.split(":")[1].strip()
                    break

        if not process_id:
            print("Skipping test: No Process ID found. Run process test first.")
            return

        # Poll until status becomes 'completed' (max 10 attempts, 3s intervals = ~30s max)
        response = search_processed_boundary(token, client, process_id, wait_for_completion=True)

        assert response.status_code == 200, f"Processed boundary search failed: {response.text}"

        data = response.json()
        resource_details = data.get("ResourceDetails", [])

        assert len(resource_details) > 0, "No processed resources found after polling"

        status = resource_details[0].get("status", "").lower()
        assert status == "completed", f"Expected status 'completed', got '{status}'"

        print(f"Found {len(resource_details)} processed resources with status 'completed'")
        processed_filestore_id = resource_details[0].get("processedFilestoreId")
        if processed_filestore_id:
            print(f"Processed FileStore ID: {processed_filestore_id}")

    except FileNotFoundError:
        print("No ids.txt file found. Run previous tests first.")
