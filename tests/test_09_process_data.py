from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest


@pytest.mark.order(9)
def test_process_data():
    """Test processing uploaded boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read required IDs
    hierarchy_type = None
    file_store_id = None

    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
            elif line.startswith("Uploaded FileStore ID:"):
                file_store_id = line.split(":")[1].strip()

    if not hierarchy_type or not file_store_id:
        pytest.skip("Missing required IDs (hierarchy type or file store ID)")

    # Load and prepare payload
    payload = load_payload("boundary_management", "process_data.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["ResourceDetails"]["tenantId"] = tenantId
    payload["ResourceDetails"]["fileStoreId"] = file_store_id
    payload["ResourceDetails"]["hierarchyType"] = hierarchy_type

    # Make API call
    response = client.post("/boundary-management/v1/_process", payload)

    assert response.status_code == 200, f"Process data failed: {response.text}"

    data = response.json()
    assert "ResourceDetails" in data
    process_id = data["ResourceDetails"]["id"]

    print(f"Boundary data processing triggered: {process_id}")

    # Save process ID
    with open("output/ids.txt", "a") as f:
        f.write(f"Process ID: {process_id}\n")
