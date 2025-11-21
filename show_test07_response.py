from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.config import tenantId
import json

def show_test07_response():
    """Show the full response from test 07"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read file store ID
    file_store_id = None
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Generated FileStore ID:"):
                file_store_id = line.split(":")[1].strip()
                break

    print(f"Generated FileStore ID: {file_store_id}\n")

    # Make API call
    url = f"/filestore/v1/files/url?tenantId={tenantId}&fileStoreIds={file_store_id}"
    print(f"API URL: {url}\n")

    response = client.get(url)

    print(f"Status Code: {response.status_code}\n")
    print("Full Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    show_test07_response()
