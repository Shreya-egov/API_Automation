from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest


@pytest.mark.order(6)
def test_generate_search():
    """Test searching for generated boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    # Load and prepare payload
    payload = load_payload("boundary_management", "generate_search.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Make API call
    url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

    assert response.status_code == 200, f"Generate search failed: {response.text}"

    data = response.json()
    assert "GeneratedResource" in data

    if len(data["GeneratedResource"]) > 0:
        resource = data["GeneratedResource"][0]
        status = resource.get("status")
        file_store_id = resource.get("fileStoreid")  # lowercase 'id'
        print(f"Status: {status}")
        if file_store_id:
            print(f"Generated file store ID: {file_store_id}")
            # Update file store ID (overwrite existing)
            with open("output/ids.txt", "r") as f:
                lines = f.readlines()

            with open("output/ids.txt", "w") as f:
                for line in lines:
                    if line.startswith("Generated FileStore ID:"):
                        f.write(f"Generated FileStore ID: {file_store_id}\n")
                    else:
                        f.write(line)
                # Add if not found
                if not any(line.startswith("Generated FileStore ID:") for line in lines):
                    f.write(f"Generated FileStore ID: {file_store_id}\n")
        else:
            print("File store ID not available yet")
    else:
        print("No generated resources found yet")
