from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
from utils.logger import setup_logger, log_test_start, log_test_end
import uuid
import allure
import json

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

    allure.attach(json.dumps(payload, indent=2), name="Search Hierarchy Request", attachment_type=allure.attachment_type.JSON)

    # Make API call with query parameters
    response = client.post(
        "/boundary-service/boundary-hierarchy-definition/_search?limit=10&offset=0",
        payload
    )

    allure.attach(f"Status Code: {response.status_code}", name="Search Hierarchy Response Status", attachment_type=allure.attachment_type.TEXT)
    allure.attach(json.dumps(response.json(), indent=2) if response.text else "No response body", name="Search Hierarchy Response Body", attachment_type=allure.attachment_type.JSON)

    return response


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

    # Store for later use (overwrite to keep only the latest)
    with open("output/ids.txt", "w") as f:
        f.write(f"Hierarchy Type: {created_type}\n")

    log_test_end(logger, "test_create_boundary_hierarchy", "PASSED")


@allure.feature("Boundary Hierarchy")
@allure.story("Search Hierarchy")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Test Search Boundary Hierarchy")
@allure.description("Searches for an existing boundary hierarchy and validates the search results")
def test_search_boundary_hierarchy():
    """Test searching for a boundary hierarchy"""
    log_test_start(logger, "test_search_boundary_hierarchy")

    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        logger.info(f"Searching for hierarchy type: {hierarchy_type}")
        response = search_boundary_hierarchy(token, client, hierarchy_type)

        assert response.status_code == 200, f"Hierarchy search failed: {response.text}"

        data = response.json()
        hierarchies = data.get("BoundaryHierarchy", [])

        assert len(hierarchies) > 0, "No hierarchies found in response"
        assert hierarchies[0]["hierarchyType"] == hierarchy_type, f"Expected {hierarchy_type}"

        logger.info(f"Hierarchy found: {hierarchies[0]['hierarchyType']}")
        logger.info(f"Number of boundary types: {len(hierarchies[0].get('boundaryHierarchy', []))}")
        print(f"Hierarchy found: {hierarchies[0]['hierarchyType']}")
        print(f"Number of boundary types: {len(hierarchies[0].get('boundaryHierarchy', []))}")

        log_test_end(logger, "test_search_boundary_hierarchy", "PASSED")

    except FileNotFoundError:
        logger.error("Hierarchy Type not found in ids.txt")
        print("No hierarchy type found. Run create test first.")
        log_test_end(logger, "test_search_boundary_hierarchy", "FAILED")
        assert False, "Hierarchy Type not found in ids.txt"
