from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import uuid


def create_boundary_hierarchy(token, client, hierarchy_type):
    """
    Helper function to create a boundary hierarchy
    Returns: hierarchyType, status_code
    """
    payload = load_payload("boundary_hierarchy", "create_hierarchy.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["BoundaryHierarchy"]["tenantId"] = tenantId
    payload["BoundaryHierarchy"]["hierarchyType"] = hierarchy_type

    # Make API call
    response = client.post("/boundary-service/boundary-hierarchy-definition/_create", payload)

    if response.status_code not in [200, 202]:
        print(f"Error creating hierarchy: {response.text}")
        return None, response.status_code

    data = response.json()
    created_hierarchy_type = data["BoundaryHierarchy"][0]["hierarchyType"]

    return created_hierarchy_type, response.status_code


def search_boundary_hierarchy(token, client, hierarchy_type):
    """
    Helper function to search boundary hierarchy
    Returns: response object
    """
    payload = load_payload("boundary_hierarchy", "search_hierarchy.json")

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["BoundaryTypeHierarchySearchCriteria"]["tenantId"] = tenantId
    payload["BoundaryTypeHierarchySearchCriteria"]["hierarchyType"] = hierarchy_type

    # Make API call with query parameters
    response = client.post(
        "/boundary-service/boundary-hierarchy-definition/_search?limit=10&offset=0",
        payload
    )

    return response


def test_create_boundary_hierarchy():
    """Test creating a boundary hierarchy"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Generate unique hierarchy type
    hierarchy_type = f"TEST_{uuid.uuid4().hex[:8].upper()}"

    created_type, status = create_boundary_hierarchy(token, client, hierarchy_type)

    assert status in [200, 202], f"Hierarchy creation failed: {status}"
    assert created_type == hierarchy_type, f"Expected {hierarchy_type}, got {created_type}"
    print(f"Boundary hierarchy created: {created_type}")

    # Store for later use
    with open("output/ids.txt", "a") as f:
        f.write(f"Hierarchy Type: {created_type}\n")


def test_search_boundary_hierarchy():
    """Test searching for a boundary hierarchy"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = search_boundary_hierarchy(token, client, hierarchy_type)

        assert response.status_code == 200, f"Hierarchy search failed: {response.text}"

        data = response.json()
        hierarchies = data.get("BoundaryHierarchy", [])

        assert len(hierarchies) > 0, "No hierarchies found in response"
        assert hierarchies[0]["hierarchyType"] == hierarchy_type, f"Expected {hierarchy_type}"

        print(f"Hierarchy found: {hierarchies[0]['hierarchyType']}")
        print(f"Number of boundary types: {len(hierarchies[0].get('boundaryHierarchy', []))}")

    except FileNotFoundError:
        print("No hierarchy type found. Run create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
