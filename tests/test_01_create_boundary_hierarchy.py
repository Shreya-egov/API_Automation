from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
from utils.logger import setup_logger, log_test_start, log_test_end
import uuid
import allure
import json
import pytest

# Set up logger
logger = setup_logger(__name__)


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

    allure.attach(json.dumps(payload, indent=2), name="Create Hierarchy Request", attachment_type=allure.attachment_type.JSON)

    # Make API call
    response = client.post("/boundary-service/boundary-hierarchy-definition/_create", payload)

    allure.attach(f"Status Code: {response.status_code}", name="Create Hierarchy Response Status", attachment_type=allure.attachment_type.TEXT)
    allure.attach(json.dumps(response.json(), indent=2) if response.text else "No response body", name="Create Hierarchy Response Body", attachment_type=allure.attachment_type.JSON)

    if response.status_code not in [200, 202]:
        print(f"Error creating hierarchy: {response.text}")
        return None, response.status_code

    data = response.json()
    created_hierarchy_type = data["BoundaryHierarchy"][0]["hierarchyType"]

    return created_hierarchy_type, response.status_code


@pytest.mark.order(1)
@allure.feature("Boundary Hierarchy")
@allure.story("Create Hierarchy")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Test Create Boundary Hierarchy")
@allure.description("Creates a new boundary hierarchy with a unique hierarchy type and validates the creation")
def test_create_boundary_hierarchy():
    """Test creating a boundary hierarchy"""
    log_test_start(logger, "test_create_boundary_hierarchy")

    token = get_auth_token("user")
    client = APIClient(token=token)

    # Generate unique hierarchy type
    hierarchy_type = f"TEST_{uuid.uuid4().hex[:8].upper()}"
    logger.info(f"Generated hierarchy type: {hierarchy_type}")

    created_type, status = create_boundary_hierarchy(token, client, hierarchy_type)

    assert status in [200, 202], f"Hierarchy creation failed: {status}"
    assert created_type == hierarchy_type, f"Expected {hierarchy_type}, got {created_type}"

    logger.info(f"Boundary hierarchy created successfully: {created_type}")
    print(f"Boundary hierarchy created: {created_type}")

    # Store for later use (overwrite to keep only the latest - this clears any old test data)
    with open("output/ids.txt", "w") as f:
        f.write(f"Hierarchy Type: {created_type}\n")

    logger.info("ids.txt file cleared and initialized with new hierarchy type")

    log_test_end(logger, "test_create_boundary_hierarchy", "PASSED")
