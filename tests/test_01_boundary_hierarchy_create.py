from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest
import uuid


@pytest.mark.order(1)
def test_boundary_hierarchy_create():
    """Test creating a boundary hierarchy"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Generate unique hierarchy type
    hierarchy_type = f"TEST_{uuid.uuid4().hex[:8].upper()}"

    # Load and prepare payload
    payload = load_payload("boundary_hierarchy", "create_hierarchy.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["BoundaryHierarchy"]["tenantId"] = tenantId
    payload["BoundaryHierarchy"]["hierarchyType"] = hierarchy_type

    # Make API call
    response = client.post("/boundary-service/boundary-hierarchy-definition/_create", payload)

    assert response.status_code == 202, f"Boundary hierarchy creation failed: {response.text}"

    data = response.json()
    assert "BoundaryHierarchy" in data
    assert data["BoundaryHierarchy"][0]["hierarchyType"] == hierarchy_type

    print(f"Boundary hierarchy created successfully: {hierarchy_type}")

    # Save hierarchy type for other tests
    with open("output/ids.txt", "w") as f:
        f.write(f"Hierarchy Type: {hierarchy_type}\n")
