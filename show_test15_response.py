import json
from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId

def show_test15_response():
    """Show full response from boundary relationship search"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    # Load and prepare payload
    payload = load_payload("boundary_relationships", "search_relationships.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["BoundaryRelationshipSearchCriteria"]["tenantId"] = tenantId
    payload["BoundaryRelationshipSearchCriteria"]["hierarchyType"] = hierarchy_type

    # Make API call with includeChildren=true
    url = f"/boundary-service/boundary-relationships/_search?tenantId={tenantId}&includeChildren=true&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

    print(f"Status Code: {response.status_code}")
    print(f"\nFull Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    show_test15_response()
