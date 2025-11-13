from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import allure
import json


def search_boundary_relationships(token, client, hierarchy_type, include_children=True):
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


def test_search_boundary_relationships():
    """Test searching boundary relationships"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = search_boundary_relationships(token, client, hierarchy_type)

        assert response.status_code == 200, f"Boundary relationships search failed: {response.text}"

        data = response.json()
        tenant_boundary = data.get("TenantBoundary", [])

        if len(tenant_boundary) > 0:
            print(f"Boundary relationships found for hierarchy: {hierarchy_type}")

            # Extract and display hierarchy structure
            boundaries = tenant_boundary[0].get("boundary", [])
            print(f"Total boundaries: {len(boundaries)}")

            # Save boundary data to file
            with open("output/boundary_relationships.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Boundary relationships saved to output/boundary_relationships.json")

            # Display sample boundary
            if len(boundaries) > 0:
                sample = boundaries[0]
                print(f"\nSample boundary:")
                print(f"  Code: {sample.get('code')}")
                print(f"  Type: {sample.get('boundaryType')}")
                print(f"  Children: {len(sample.get('children', []))}")
        else:
            print("No boundary relationships found. The hierarchy may not have boundary data yet.")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"


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
