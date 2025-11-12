from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import time


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
    response = client.post(url, payload)

    if response.status_code not in [200, 202]:
        print(f"Error generating boundary data: {response.text}")
        return None, response.status_code

    data = response.json()
    resource_id = data.get("ResourceDetails", {}).get("id")

    return resource_id, response.status_code


def search_generated_boundary(token, client, hierarchy_type):
    """
    Helper function to search for generated boundary data
    Returns: response object
    """
    payload = load_payload("boundary_management", "generate_search.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Make API call with query parameters
    url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

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

    # Make API call
    response = client.post("/boundary-management/v1/_process", payload)

    if response.status_code not in [200, 202]:
        print(f"Error processing boundary data: {response.text}")
        return None, response.status_code

    data = response.json()
    process_id = data.get("ResourceDetails", {}).get("id")

    return process_id, response.status_code


def search_processed_boundary(token, client, process_id):
    """
    Helper function to search for processed boundary data
    Returns: response object
    """
    payload = load_payload("boundary_management", "process_search.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["SearchCriteria"]["id"] = [process_id]
    payload["SearchCriteria"]["tenantId"] = tenantId

    # Make API call
    response = client.post("/boundary-management/v1/_process-search", payload)

    return response


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


def test_search_generated_boundary():
    """Test searching for generated boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        # Wait a bit for generation to complete
        time.sleep(2)

        response = search_generated_boundary(token, client, hierarchy_type)

        assert response.status_code == 200, f"Generated boundary search failed: {response.text}"

        data = response.json()
        generated_resources = data.get("GeneratedResource", [])

        if len(generated_resources) > 0:
            print(f"Found {len(generated_resources)} generated resources")
            filestore_id = generated_resources[0].get("fileStoreId")
            print(f"FileStore ID: {filestore_id}")

            # Store filestore ID for later use
            if filestore_id:
                with open("output/ids.txt", "a") as f:
                    f.write(f"FileStore ID: {filestore_id}\n")
        else:
            print("No generated resources found yet. Generation may still be in progress.")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"


def test_process_boundary_data():
    """Test processing boundary data (requires fileStoreId from file upload)"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # This test requires a fileStoreId from a file upload
    # For now, we'll skip if no fileStoreId is available
    try:
        hierarchy_type = None
        file_store_id = None

        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                elif line.startswith("FileStore ID:"):
                    file_store_id = line.split(":")[1].strip()

        if not file_store_id:
            print("Skipping test: No FileStore ID found. Upload a file first.")
            return

        if not hierarchy_type:
            print("Skipping test: No Hierarchy Type found.")
            return

        process_id, status = process_boundary_data(token, client, file_store_id, hierarchy_type)

        assert status in [200, 202], f"Boundary data processing failed: {status}"
        assert process_id is not None, "Process ID not returned"

        print(f"Boundary data processing triggered. Process ID: {process_id}")

        # Store for later use
        with open("output/ids.txt", "a") as f:
            f.write(f"Process ID: {process_id}\n")

    except FileNotFoundError:
        print("No ids.txt file found. Run previous tests first.")


def test_search_processed_boundary():
    """Test searching for processed boundary data"""
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

        # Wait a bit for processing to complete
        time.sleep(2)

        response = search_processed_boundary(token, client, process_id)

        assert response.status_code == 200, f"Processed boundary search failed: {response.text}"

        data = response.json()
        resource_details = data.get("ResourceDetails", [])

        if len(resource_details) > 0:
            print(f"Found {len(resource_details)} processed resources")
            processed_filestore_id = resource_details[0].get("processedFilestoreId")
            status = resource_details[0].get("status")
            print(f"Status: {status}")
            if processed_filestore_id:
                print(f"Processed FileStore ID: {processed_filestore_id}")
        else:
            print("No processed resources found yet. Processing may still be in progress.")

    except FileNotFoundError:
        print("No ids.txt file found. Run previous tests first.")
