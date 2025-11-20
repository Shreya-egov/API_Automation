from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import allure
import json
import pytest


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


@pytest.mark.order(5)
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

        # Store for later use - replace old Generate Resource ID if exists
        with open("output/ids.txt", "r") as f:
            lines = f.readlines()

        # Remove old Generate Resource ID lines
        lines = [line for line in lines if not line.startswith("Generate Resource ID:")]

        # Write back with new Generate Resource ID
        with open("output/ids.txt", "w") as f:
            f.writelines(lines)
            f.write(f"Generate Resource ID: {resource_id}\n")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
