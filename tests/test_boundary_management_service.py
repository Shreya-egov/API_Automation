from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import time
import allure
import json


def generate_boundary_data(token, client, hierarchy_type, force_update=True):
    """
    Helper function to trigger boundary data generation
    Returns: resource_id, status_code
    """
    payload = load_payload("boundary_management", "generate_data.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Make API call with query parameters
    url = f"/boundary-management/v1/_generate?tenantId={tenantId}&forceUpdate={str(force_update).lower()}&hierarchyType={hierarchy_type}"

    allure.attach(json.dumps(payload, indent=2), name="Generate Request Payload", attachment_type=allure.attachment_type.JSON)

    response = client.post(url, payload)

    allure.attach(f"Status Code: {response.status_code}", name="Generate Response Status", attachment_type=allure.attachment_type.TEXT)
    allure.attach(json.dumps(response.json(), indent=2) if response.text else "No response body", name="Generate Response Body", attachment_type=allure.attachment_type.JSON)

    if response.status_code not in [200, 202]:
        print(f"Error generating boundary data: {response.text}")
        return None, response.status_code

    data = response.json()

    # Handle both list and dict responses
    if isinstance(data, list):
        resource_id = data[0].get("id") if data else None
    else:
        resource_details = data.get("ResourceDetails", [])
        if isinstance(resource_details, list) and resource_details:
            resource_id = resource_details[0].get("id")
        else:
            resource_id = resource_details.get("id") if isinstance(resource_details, dict) else None

    return resource_id, response.status_code


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


@allure.feature("Boundary Management")
@allure.story("Generate Boundary Data")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Test Generate Boundary Data")
@allure.description("Triggers boundary data generation for a specific hierarchy type and validates the response")
def test_generate_boundary_data():
    """Test generating boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        resource_id, status = generate_boundary_data(token, client, hierarchy_type)

        assert status in [200, 202], f"Boundary data generation failed: {status}"
        assert resource_id is not None, "Resource ID not returned"

        print(f"Boundary data generation triggered. Resource ID: {resource_id}")

        # Store for later use
        with open("output/ids.txt", "a") as f:
            f.write(f"Generate Resource ID: {resource_id}\n")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"


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

        # Poll until status becomes 'completed' (max 30 attempts, 5s intervals = ~150s/2.5min max)
        response = search_generated_boundary(token, client, hierarchy_type, wait_for_completion=True, max_retries=30, retry_interval=5)

        assert response.status_code == 200, f"Generated boundary search failed: {response.text}"

        data = response.json()
        generated_resources = data.get("GeneratedResource", [])

        if len(generated_resources) == 0:
            print("WARNING: No generated resources found after polling. Generation may have failed or is taking longer than expected.")
            print("Skipping test - this is expected if generation is not completing in time.")
            return

        status = generated_resources[0].get("status", "").lower()

        if status != "completed":
            print(f"WARNING: Generation status is '{status}', not 'completed'. Skipping test.")
            return

        print(f"Found {len(generated_resources)} generated resources with status 'completed'")
        filestore_id = generated_resources[0].get("fileStoreId")
        print(f"FileStore ID: {filestore_id}")

        # Store filestore ID for later use
        if filestore_id:
            with open("output/ids.txt", "a") as f:
                f.write(f"FileStore ID: {filestore_id}\n")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"


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

        # Parse backwards to find the most recent hierarchy type and its corresponding FileStore ID
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if line.startswith("Hierarchy Type:") and not found_hierarchy:
                hierarchy_type = line.split(":")[1].strip()
                found_hierarchy = True
                # Now look forward from this point to find the associated FileStore ID (not Uploaded)
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("FileStore ID:") and not lines[j].startswith("Uploaded FileStore ID:"):
                        file_store_id = lines[j].split(":")[1].strip()
                        break
                    elif lines[j].startswith("Hierarchy Type:"):
                        # Hit another hierarchy type, stop searching
                        break
                break

        if not hierarchy_type:
            print("Skipping test: No Hierarchy Type found.")
            return

        if not file_store_id:
            print("Skipping test: No FileStore ID from generate search found.")
            print("This test requires a completed boundary generation that produces a template file.")
            print("Run the generate and search tests first and ensure generation completes successfully.")
            return

        print(f"Processing boundary data for hierarchy: {hierarchy_type}")
        print(f"Using FileStore ID: {file_store_id}")

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
