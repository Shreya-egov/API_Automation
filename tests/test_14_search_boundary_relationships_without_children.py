from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import allure
import json
import pytest


def search_boundary_relationships(token, client, hierarchy_type, include_children=False):
    """
    Helper function to search boundary relationships
    Returns: response object
    """
    payload = load_payload("boundary_relationships", "search_relationships.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)

    # Make API call with query parameters
    url = f"/boundary-service/boundary-relationships/_search?tenantId={tenantId}&includeChildren={str(include_children).lower()}&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

    return response


@pytest.mark.order(14)
@allure.feature("Boundary Relationships")
@allure.story("Search Relationships")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Test Search Boundary Relationships without Children")
@allure.description("Searches for boundary relationships excluding child boundaries in the hierarchy")
def test_search_boundary_relationships_without_children():
    """Test searching boundary relationships without children"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = search_boundary_relationships(token, client, hierarchy_type, include_children=False)

        assert response.status_code == 200, f"Boundary relationships search failed: {response.text}"

        data = response.json()
        tenant_boundary = data.get("TenantBoundary", [])

        if len(tenant_boundary) > 0:
            boundaries = tenant_boundary[0].get("boundary", [])
            print(f"Boundary relationships found (without children): {len(boundaries)} boundaries")
        else:
            print("No boundary relationships found.")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
