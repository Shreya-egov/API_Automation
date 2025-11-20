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
        file_store_id = data["GeneratedResource"][0].get("fileStoreid")
        if file_store_id:
            print(f"Generated file store ID: {file_store_id}")
            with open("output/ids.txt", "a") as f:
                f.write(f"Generated FileStore ID: {file_store_id}\n")
    else:
        print("No generated resources found yet")
